"""
Test Multi-Language Code Execution Services
"""

import pytest
import json
from app.grpc_services.executor_client import CodeExecutorClient
from app.grpc_services.python_executor import PythonExecutorService
from app.grpc_services.r_executor import RExecutorService
from app.grpc_services.matlab_executor import MatlabExecutorService


class TestPythonExecutor:
    """Test Python code execution"""

    def test_simple_function(self):
        """Test basic Python function execution"""
        service = PythonExecutorService()

        code = """
def add(a, b):
    return a + b
"""

        request = type('obj', (object,), {
            'code': code,
            'function_name': 'add',
            'test_cases': [
                type('obj', (object,), {
                    'input_json': json.dumps([2, 3]),
                    'expected_output': json.dumps(5),
                    'timeout_ms': 5000
                })(),
            ],
            'solution_code': code,
            'memory_limit_mb': 256,
            'cpu_limit_percent': 50
        })()

        result = service.ExecuteCode(request, None)

        assert result['success'] == True
        assert result['all_tests_passed'] == True
        assert result['passed_tests'] == 1

    def test_list_operations(self):
        """Test Python list operations"""
        service = PythonExecutorService()

        code = """
def sum_list(numbers):
    return sum(numbers)
"""

        request = type('obj', (object,), {
            'code': code,
            'function_name': 'sum_list',
            'test_cases': [
                type('obj', (object,), {
                    'input_json': json.dumps([[1, 2, 3, 4, 5]]),
                    'expected_output': json.dumps(15),
                    'timeout_ms': 5000
                })(),
                type('obj', (object,), {
                    'input_json': json.dumps([[10, 20, 30]]),
                    'expected_output': json.dumps(60),
                    'timeout_ms': 5000
                })(),
            ],
            'solution_code': code,
            'memory_limit_mb': 256,
            'cpu_limit_percent': 50
        })()

        result = service.ExecuteCode(request, None)

        assert result['success'] == True
        assert result['all_tests_passed'] == True
        assert result['passed_tests'] == 2

    def test_syntax_validation(self):
        """Test Python syntax validation"""
        service = PythonExecutorService()

        # Valid code
        request = type('obj', (object,), {
            'code': 'def test(): return 1',
            'language': 1
        })()

        result = service.ValidateSyntax(request, None)
        assert result['is_valid'] == True

        # Invalid code
        request = type('obj', (object,), {
            'code': 'def test( return 1',  # Syntax error
            'language': 1
        })()

        result = service.ValidateSyntax(request, None)
        assert result['is_valid'] == False
        assert len(result['syntax_errors']) > 0

    def test_language_info(self):
        """Test getting Python language info"""
        service = PythonExecutorService()

        request = type('obj', (object,), {
            'language': 1
        })()

        result = service.GetLanguageInfo(request, None)

        assert result['is_available'] == True
        assert result['language'] == 1
        assert 'version' in result


class TestRExecutor:
    """Test R code execution"""

    def test_simple_function(self):
        """Test basic R function execution"""
        service = RExecutorService()

        if not service.r_executable:
            pytest.skip("R not installed")

        code = """
add <- function(a, b) {
    return(a + b)
}
"""

        request = type('obj', (object,), {
            'code': code,
            'function_name': 'add',
            'test_cases': [
                type('obj', (object,), {
                    'input_json': json.dumps([2, 3]),
                    'expected_output': json.dumps(5),
                    'timeout_ms': 5000
                })(),
            ],
            'solution_code': code,
            'memory_limit_mb': 256
        })()

        result = service.ExecuteCode(request, None)

        assert result['success'] == True

    def test_vector_operations(self):
        """Test R vector operations"""
        service = RExecutorService()
        
        if not service.r_executable:
            pytest.skip("R not installed")

        code = """
vector_sum <- function(vec) {
    return(sum(vec))
}
"""

        request = type('obj', (object,), {
            'code': code,
            'function_name': 'vector_sum',
            'test_cases': [
                type('obj', (object,), {
                    'input_json': json.dumps([[1, 2, 3, 4, 5]]),
                    'expected_output': json.dumps(15),
                    'timeout_ms': 5000
                })(),
            ],
            'solution_code': code,
            'memory_limit_mb': 256
        })()

        result = service.ExecuteCode(request, None)

        assert result['success'] == True

    def test_language_info(self):
        """Test getting R language info"""
        service = RExecutorService()

        request = type('obj', (object,), {
            'language': 2
        })()

        result = service.GetLanguageInfo(request, None)

        assert result['language'] == 2
        assert 'version' in result


class TestMatlabExecutor:
    """Test MATLAB/Octave code execution"""

    def test_simple_function(self):
        """Test basic MATLAB function execution"""
        service = MatlabExecutorService()

        if not service.matlab_executable:
            pytest.skip("MATLAB/Octave not installed")

        code = """
function result = add(a, b)
    result = a + b;
end
"""

        request = type('obj', (object,), {
            'code': code,
            'function_name': 'add',
            'test_cases': [
                type('obj', (object,), {
                    'input_json': json.dumps([2, 3]),
                    'expected_output': json.dumps(5),
                    'timeout_ms': 5000
                })(),
            ],
            'solution_code': code,
            'memory_limit_mb': 512
        })()

        result = service.ExecuteCode(request, None)

        assert result['success'] == True

    def test_language_info(self):
        """Test getting MATLAB language info"""
        service = MatlabExecutorService()

        request = type('obj', (object,), {
            'language': 3
        })()

        result = service.GetLanguageInfo(request, None)

        assert result['language'] == 3
        assert 'version' in result


class TestExecutorClient:
    """Test unified executor client"""

    def test_python_execution(self):
        """Test Python execution via client"""
        client = CodeExecutorClient()

        result = client.execute_code(
            language='python',
            code='def double(x): return x * 2',
            function_name='double',
            test_cases=[
                {'input': [5], 'expected_output': 10},
                {'input': [10], 'expected_output': 20},
            ]
        )

        assert result['success'] == True
        assert result['passed_tests'] == 2

    def test_multiple_test_cases(self):
        """Test execution with multiple test cases"""
        client = CodeExecutorClient()

        result = client.execute_code(
            language='python',
            code='def is_even(n): return n % 2 == 0',
            function_name='is_even',
            test_cases=[
                {'input': [2], 'expected_output': True},
                {'input': [3], 'expected_output': False},
                {'input': [4], 'expected_output': True},
                {'input': [7], 'expected_output': False},
            ]
        )

        assert result['success'] == True
        assert result['total_tests'] == 4
        assert result['passed_tests'] == 4

    def test_syntax_validation(self):
        """Test syntax validation via client"""
        client = CodeExecutorClient()

        # Valid Python
        result = client.validate_syntax('python', 'def test(): return 1')
        assert result['is_valid'] == True

        # Invalid Python
        result = client.validate_syntax('python', 'def test( return 1')
        assert result['is_valid'] == False

    def test_language_info(self):
        """Test getting language information"""
        client = CodeExecutorClient()

        info = client.get_language_info('python')

        assert info['is_available'] == True
        assert 'version' in info

    def test_error_handling(self):
        """Test error handling for invalid code"""
        client = CodeExecutorClient()

        result = client.execute_code(
            language='python',
            code='def broken_func(): raise ValueError("Test error")',
            function_name='broken_func',
            test_cases=[
                {'input': [], 'expected_output': None},
            ]
        )

        assert result['success'] == False or result['all_tests_passed'] == False


class TestComparison:
    """Test output comparison logic"""

    def test_float_comparison(self):
        """Test float comparison with tolerance"""
        service = PythonExecutorService()

        # Test that floats are compared with tolerance
        assert service._compare_outputs(3.14159, 3.14159) == True
        assert service._compare_outputs(3.14159, 3.14160) == False
        assert service._compare_outputs(1.0, 1.0000001) == False

    def test_list_comparison(self):
        """Test list comparison"""
        service = PythonExecutorService()

        assert service._compare_outputs([1, 2, 3], [1, 2, 3]) == True
        assert service._compare_outputs([1, 2, 3], [1, 2, 4]) == False
        assert service._compare_outputs([1, 2], [1, 2, 3]) == False

    def test_dict_comparison(self):
        """Test dictionary comparison"""
        service = PythonExecutorService()

        assert service._compare_outputs({'a': 1, 'b': 2}, {'a': 1, 'b': 2}) == True
        assert service._compare_outputs({'a': 1}, {'a': 1, 'b': 2}) == False
        assert service._compare_outputs({'a': 1}, {'b': 2}) == False


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_fibonacci_python(self):
        """Test Fibonacci implementation in Python"""
        client = CodeExecutorClient()

        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

        result = client.execute_code(
            language='python',
            code=code,
            function_name='fibonacci',
            test_cases=[
                {'input': [0], 'expected_output': 0},
                {'input': [1], 'expected_output': 1},
                {'input': [5], 'expected_output': 5},
                {'input': [10], 'expected_output': 55},
            ]
        )

        assert result['all_tests_passed'] == True
        assert result['passed_tests'] == 4

    def test_factorial_python(self):
        """Test factorial implementation in Python"""
        client = CodeExecutorClient()

        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""

        result = client.execute_code(
            language='python',
            code=code,
            function_name='factorial',
            test_cases=[
                {'input': [0], 'expected_output': 1},
                {'input': [1], 'expected_output': 1},
                {'input': [5], 'expected_output': 120},
                {'input': [7], 'expected_output': 5040},
            ]
        )


