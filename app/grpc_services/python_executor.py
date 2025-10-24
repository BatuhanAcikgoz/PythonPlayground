"""
Python Code Executor Service - gRPC Server Implementation
Handles Python code execution in isolated environment
"""

import grpc
from concurrent import futures
import sys
import io
import json
import time
import traceback
import resource
import signal
import re
import os
from contextlib import contextmanager

# Add generated proto files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

# Import generated proto files
import code_executor_pb2
import code_executor_pb2_grpc


class TimeoutException(Exception):
    """Raised when code execution times out"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutException("Code execution timed out")


def check_indentation(code: str):
    """Kod içindeki girinti hatalarını ve sözdizimi hatalarını kontrol eder"""
    lines = code.splitlines()

    # Tab ve boşluk karışımını kontrol et
    for i, line in enumerate(lines):
        if line.strip() and line.startswith(" ") and "\t" in line:
            return False, i + 1, "Bu satırda hem tab hem de boşluk karakteri var, bu tutarsız girintiye neden olur", "indentation"

    # Girinti tutarlılığını ve sözdizimi hatalarını kontrol et
    try:
        # Gerçek Python derleyicisiyle girinti ve sözdizimi hatalarını tespit et
        compile(code, "<string>", "exec")
        return True, None, None, None
    except IndentationError as e:
        # IndentationError, satır numarasını ve hata mesajını içerir
        return False, e.lineno, str(e), "indentation"
    except SyntaxError as e:
        # SyntaxError hatalarını da yakala
        return False, e.lineno, str(e), "syntax"
    except Exception as e:
        # Diğer hatalar için
        return False, None, str(e), "other"


def normalize_indentation(code: str) -> str:
    """Kod içindeki karışık girintileri normalleştirip tutarlı hale getirir"""
    lines = code.splitlines()
    normalized_lines = []

    # Her satır için
    for line in lines:
        if line.strip():  # Boş satır değilse
            # Satırın başındaki boşlukları say
            leading_space_count = len(line) - len(line.lstrip())
            leading_content = line[:leading_space_count]

            # Tab ve boşluk karışımını kontrol et ve düzelt
            if '\t' in leading_content and ' ' in leading_content:
                # Her tab'ı 4 boşlukla değiştir (Python standardı)
                fixed_indent = leading_content.replace('\t', '    ')
                normalized_lines.append(fixed_indent + line[leading_space_count:])
            elif '\t' in leading_content:
                # Tüm tab'ları 4 boşlukla değiştir
                fixed_indent = leading_content.replace('\t', '    ')
                normalized_lines.append(fixed_indent + line[leading_space_count:])
            else:
                normalized_lines.append(line)
        else:
            normalized_lines.append(line)

    return '\n'.join(normalized_lines)


def inject_random_seed(code: str, function_name: str) -> str:
    """Random modülü kullanıldığında seed ekler"""
    if not code:
        return code

    # Random kullanım kontrolü
    uses_random = re.search(r'import\s+random|from\s+random\s+import', code) is not None

    if uses_random:
        # Fonksiyon tanımını bul
        function_pattern = re.compile(f"def\\s+{re.escape(function_name)}\\s*\\([^)]*\\)\\s*:")
        match = function_pattern.search(code)
        if match:
            insertion_point = match.end()
            # Fonksiyonun ilk satırına seed enjekte et
            code = code[:insertion_point] + "\n    random.seed(67)" + code[insertion_point:]

    return code


@contextmanager
def execution_environment(memory_limit_mb=256, timeout_seconds=5):
    """
    Create isolated execution environment with resource limits
    
    Args:
        memory_limit_mb: Memory limit in megabytes
        timeout_seconds: Execution timeout in seconds
    """
    # Set memory limit (soft and hard)
    memory_limit = memory_limit_mb * 1024 * 1024  # Convert to bytes
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
    
    # Set CPU time limit
    resource.setrlimit(resource.RLIMIT_CPU, (timeout_seconds, timeout_seconds))
    
    # Set timeout alarm
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        yield
    finally:
        # Cancel alarm
        signal.alarm(0)


class PythonExecutorService(code_executor_pb2_grpc.CodeExecutorServiceServicer):
    """Python code executor implementing gRPC service"""
    
    def ExecuteCode(self, request, context):
        """
        Execute Python code with test cases
        
        Args:
            request: ExecutionRequest from proto
            context: gRPC context
            
        Returns:
            ExecutionResponse with test results
        """
        start_time = time.time()
        test_results = []
        errors = []
        all_passed = True
        
        try:
            # 1. Kod ön işleme ve kontrol
            normalized_code = normalize_indentation(request.code)

            # 2. Geliştirilmiş girinti kontrolü
            is_valid, line_num, error_msg, error_type = check_indentation(normalized_code)
            if not is_valid:
                if error_type == "syntax":
                    errors.append(f"Satır {line_num}'de sözdizimi hatası: {error_msg}")
                elif error_type == "indentation":
                    errors.append(f"Satır {line_num}'de girinti hatası: {error_msg}")
                else:
                    errors.append(f"Kodda hata: {error_msg}")
                return self._create_error_response(errors[0])

            # 3. Random kullanım kontrolü ve seed enjeksiyonu
            normalized_code = inject_random_seed(normalized_code, request.function_name)

            # 4. Parse and validate the code
            code_namespace = {}
            exec(normalized_code, code_namespace)

            # 5. Get the function
            if request.function_name not in code_namespace:
                return self._create_error_response(
                    f"Function '{request.function_name}' not found in code"
                )
            
            user_function = code_namespace[request.function_name]
            
            if not callable(user_function):
                return self._create_error_response(
                    f"'{request.function_name}' is not a callable function"
                )

            # 6. Execute each test case
            for idx, test_case in enumerate(request.test_cases):
                test_result = self._execute_test_case(
                    user_function,
                    test_case,
                    request.memory_limit_mb or 256,
                    request.function_name
                )
                test_results.append(test_result)
                
                if not test_result.passed:
                    all_passed = False
                    
        except SyntaxError as e:
            errors.append(f"Syntax Error: {str(e)}")
            all_passed = False
        except Exception as e:
            errors.append(f"Execution Error: {str(e)}\n{traceback.format_exc()}")
            all_passed = False
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return code_executor_pb2.ExecutionResponse(
            success=len(errors) == 0,
            all_tests_passed=all_passed,
            total_tests=len(request.test_cases),
            passed_tests=sum(1 for r in test_results if r.passed),
            failed_tests=sum(1 for r in test_results if not r.passed),
            test_results=test_results,
            total_execution_time_ms=total_time,
            errors=errors,
            stdout='',
            stderr=''
        )

    def _execute_test_case(self, function, test_case, memory_limit_mb, function_name):
        """Execute a single test case"""
        start_time = time.time()
        
        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        
        try:
            # Parse input
            test_input = json.loads(test_case.input_json)
            expected = json.loads(test_case.expected_output)
            
            # Execute with timeout and memory limits
            timeout_seconds = (test_case.timeout_ms or 5000) / 1000
            
            with execution_environment(memory_limit_mb, int(timeout_seconds)):
                if isinstance(test_input, list):
                    actual_output = function(*test_input)
                else:
                    actual_output = function(test_input)
            
            execution_time = (time.time() - start_time) * 1000
            
            # Compare outputs
            passed = self._compare_outputs(expected, actual_output)
            
            return code_executor_pb2.TestResult(
                passed=passed,
                input=test_case.input_json,
                expected_output=json.dumps(expected),
                actual_output=json.dumps(actual_output),
                error_message='' if passed else 'Output mismatch',
                execution_time_ms=execution_time,
                memory_used_mb=0  # TODO: Implement memory tracking
            )

        except TimeoutException:
            return code_executor_pb2.TestResult(
                passed=False,
                input=test_case.input_json,
                expected_output=test_case.expected_output,
                actual_output='',
                error_message='Execution timeout',
                execution_time_ms=(test_case.timeout_ms or 5000),
                memory_used_mb=0
            )
        except Exception as e:
            return code_executor_pb2.TestResult(
                passed=False,
                input=test_case.input_json,
                expected_output=test_case.expected_output,
                actual_output='',
                error_message=f"{type(e).__name__}: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000,
                memory_used_mb=0
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _compare_outputs(self, expected, actual):
        """Compare expected and actual outputs with tolerance for floats"""
        if type(expected) != type(actual):
            return False
        
        if isinstance(expected, float):
            return abs(expected - actual) < 1e-6
        elif isinstance(expected, list):
            if len(expected) != len(actual):
                return False
            return all(self._compare_outputs(e, a) for e, a in zip(expected, actual))
        elif isinstance(expected, dict):
            if set(expected.keys()) != set(actual.keys()):
                return False
            return all(self._compare_outputs(expected[k], actual[k]) for k in expected.keys())
        else:
            return expected == actual
    
    def _create_error_response(self, error_message):
        """Create an error response"""
        return code_executor_pb2.ExecutionResponse(
            success=False,
            all_tests_passed=False,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            test_results=[],
            total_execution_time_ms=0,
            errors=[error_message],
            stdout='',
            stderr=''
        )

    def ValidateSyntax(self, request, context):
        """Validate Python syntax without execution"""
        try:
            # Normalize and check indentation
            normalized_code = normalize_indentation(request.code)
            is_valid, line_num, error_msg, error_type = check_indentation(normalized_code)

            if not is_valid:
                return code_executor_pb2.ValidationResponse(
                    is_valid=False,
                    syntax_errors=[f"Line {line_num}: {error_msg}"],
                    warnings=[]
                )

            return code_executor_pb2.ValidationResponse(
                is_valid=True,
                syntax_errors=[],
                warnings=[]
            )
        except SyntaxError as e:
            return code_executor_pb2.ValidationResponse(
                is_valid=False,
                syntax_errors=[f"Line {e.lineno}: {e.msg}"],
                warnings=[]
            )

    def GetLanguageInfo(self, request, context):
        """Get Python language information"""
        return code_executor_pb2.LanguageInfoResponse(
            language=code_executor_pb2.PYTHON,
            version=sys.version,
            available_packages=['numpy', 'pandas', 'scipy', 'matplotlib'],
            is_available=True
        )


def serve(port=50051):
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    code_executor_pb2_grpc.add_CodeExecutorServiceServicer_to_server(
        PythonExecutorService(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Python Executor gRPC Server started on port {port}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
