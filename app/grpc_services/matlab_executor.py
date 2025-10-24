"""
MATLAB Code Executor Service - gRPC Server Implementation
Handles MATLAB code execution in isolated environment
"""

import subprocess
import json
import time
import tempfile
import os


class MatlabExecutorService:
    """MATLAB code executor implementing gRPC service"""
    
    def __init__(self):
        self.matlab_executable = self._find_matlab_executable()
    
    def _find_matlab_executable(self):
        """Find MATLAB executable in system"""
        for cmd in ['matlab', 'octave']:  # Octave as fallback
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        return None
    
    def ExecuteCode(self, request, context):
        """Execute MATLAB code with test cases"""
        if not self.matlab_executable:
            return self._create_error_response("MATLAB/Octave interpreter not found")
        
        start_time = time.time()
        test_results = []
        errors = []
        all_passed = True
        
        try:
            # Execute each test case
            for idx, test_case in enumerate(request.test_cases):
                test_result = self._execute_test_case(
                    request.code,
                    test_case,
                    request.function_name
                )
                test_results.append(test_result)
                
                if not test_result['passed']:
                    all_passed = False
                    
        except Exception as e:
            errors.append(f"Execution Error: {str(e)}")
            all_passed = False
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            'success': len(errors) == 0,
            'all_tests_passed': all_passed,
            'total_tests': len(request.test_cases),
            'passed_tests': sum(1 for r in test_results if r['passed']),
            'failed_tests': sum(1 for r in test_results if not r['passed']),
            'test_results': test_results,
            'total_execution_time_ms': total_time,
            'errors': errors,
            'stdout': '',
            'stderr': ''
        }
    
    def _create_matlab_script(self, user_code, test_case, function_name):
        """Create MATLAB script for execution"""
        return f"""
% User submitted code
{user_code}

% Parse test input
input_json = '{test_case.input_json}';
input_data = jsondecode(input_json);

% Execute function
if iscell(input_data)
    result = {function_name}(input_data{{:}});
else
    result = {function_name}(input_data);
end

% Convert result to JSON and display
result_json = jsonencode(result);
disp(result_json);
"""
    
    def _execute_test_case(self, user_code, test_case, function_name):
        """Execute a single test case in MATLAB"""
        start_time = time.time()
        
        try:
            # Create MATLAB script
            matlab_script = self._create_matlab_script(user_code, test_case, function_name)
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.m', delete=False) as f:
                f.write(matlab_script)
                script_path = f.name
            
            # Execute MATLAB script
            timeout_seconds = (test_case.timeout_ms or 5000) / 1000
            
            if self.matlab_executable == 'matlab':
                cmd = [
                    self.matlab_executable,
                    '-nodisplay', '-nosplash', '-nodesktop',
                    '-r', f"run('{script_path}'); exit;"
                ]
            else:  # octave
                cmd = [self.matlab_executable, '--quiet', '--eval', f"run('{script_path}')"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Parse output
            if result.returncode == 0:
                # Extract JSON from output (MATLAB may add extra output)
                output_lines = result.stdout.strip().split('\n')
                actual_output = output_lines[-1]  # Last line should be JSON
                
                try:
                    expected = json.loads(test_case.expected_output)
                    actual = json.loads(actual_output)
                    
                    passed = self._compare_outputs(expected, actual)
                    
                    return {
                        'passed': passed,
                        'input': test_case.input_json,
                        'expected_output': test_case.expected_output,
                        'actual_output': actual_output,
                        'error_message': '' if passed else 'Output mismatch',
                        'execution_time_ms': execution_time,
                        'memory_used_mb': 0
                    }
                except json.JSONDecodeError:
                    return {
                        'passed': False,
                        'input': test_case.input_json,
                        'expected_output': test_case.expected_output,
                        'actual_output': actual_output,
                        'error_message': 'Invalid JSON output',
                        'execution_time_ms': execution_time,
                        'memory_used_mb': 0
                    }
            else:
                return {
                    'passed': False,
                    'input': test_case.input_json,
                    'expected_output': test_case.expected_output,
                    'actual_output': '',
                    'error_message': result.stderr,
                    'execution_time_ms': execution_time,
                    'memory_used_mb': 0
                }
                
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'input': test_case.input_json,
                'expected_output': test_case.expected_output,
                'actual_output': '',
                'error_message': 'Execution timeout',
                'execution_time_ms': test_case.timeout_ms or 5000,
                'memory_used_mb': 0
            }
        except Exception as e:
            return {
                'passed': False,
                'input': test_case.input_json,
                'expected_output': test_case.expected_output,
                'actual_output': '',
                'error_message': str(e),
                'execution_time_ms': (time.time() - start_time) * 1000,
                'memory_used_mb': 0
            }
        finally:
            # Clean up temp file
            if os.path.exists(script_path):
                os.unlink(script_path)
    
    def _compare_outputs(self, expected, actual):
        """Compare expected and actual outputs with tolerance for floats"""
        if type(expected) != type(actual):
            return False
        
        if isinstance(expected, float):
            return abs(expected - actual) < 1e-6
        elif isinstance(expected, (list, tuple)):
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
        return {
            'success': False,
            'all_tests_passed': False,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': [],
            'total_execution_time_ms': 0,
            'errors': [error_message],
            'stdout': '',
            'stderr': ''
        }
    
    def ValidateSyntax(self, request, context):
        """Validate MATLAB syntax"""
        # MATLAB syntax validation is tricky, we'll do basic check
        return {
            'is_valid': True,
            'syntax_errors': [],
            'warnings': ['Syntax validation not fully implemented for MATLAB']
        }
    
    def GetLanguageInfo(self, request, context):
        """Get MATLAB language information"""
        try:
            result = subprocess.run(
                [self.matlab_executable, '--version'],
                capture_output=True,
                text=True
            )
            version = result.stdout.split('\n')[0] if result.returncode == 0 else 'Unknown'
        except:
            version = 'Unknown'
        
        return {
            'language': 3,  # MATLAB
            'version': version,
            'available_packages': [],
            'is_available': self.matlab_executable is not None
        }
"""
R Code Executor Service - gRPC Server Implementation
Handles R code execution in isolated environment
"""

import subprocess
import json
import time
import tempfile
import os
from pathlib import Path


class RExecutorService:
    """R code executor implementing gRPC service"""
    
    def __init__(self):
        self.r_executable = self._find_r_executable()
    
    def _find_r_executable(self):
        """Find R executable in system"""
        for cmd in ['Rscript', 'R']:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        return None
    
    def ExecuteCode(self, request, context):
        """Execute R code with test cases"""
        if not self.r_executable:
            return self._create_error_response("R interpreter not found")
        
        start_time = time.time()
        test_results = []
        errors = []
        all_passed = True
        
        try:
            # Create R script wrapper
            r_script = self._create_r_script(request)
            
            # Execute each test case
            for idx, test_case in enumerate(request.test_cases):
                test_result = self._execute_test_case(
                    r_script,
                    test_case,
                    request.function_name
                )
                test_results.append(test_result)
                
                if not test_result['passed']:
                    all_passed = False
                    
        except Exception as e:
            errors.append(f"Execution Error: {str(e)}")
            all_passed = False
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            'success': len(errors) == 0,
            'all_tests_passed': all_passed,
            'total_tests': len(request.test_cases),
            'passed_tests': sum(1 for r in test_results if r['passed']),
            'failed_tests': sum(1 for r in test_results if not r['passed']),
            'test_results': test_results,
            'total_execution_time_ms': total_time,
            'errors': errors,
            'stdout': '',
            'stderr': ''
        }
    
    def _create_r_script(self, request):
        """Create R script from user code"""
        return f"""
# User submitted code
{request.code}

# Test execution wrapper
execute_test <- function(input_json, function_name) {{
    input_data <- jsonlite::fromJSON(input_json)
    
    # Call user function
    if (is.list(input_data)) {{
        result <- do.call(get(function_name), input_data)
    }} else {{
        result <- get(function_name)(input_data)
    }}
    
    return(jsonlite::toJSON(result, auto_unbox = TRUE))
}}
"""
    
    def _execute_test_case(self, r_script, test_case, function_name):
        """Execute a single test case in R"""
        start_time = time.time()
        
        try:
            # Create temporary R script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
                f.write(r_script)
                f.write(f"\n\n# Execute test\n")
                f.write(f"input_json <- '{test_case.input_json}'\n")
                f.write(f"result <- execute_test(input_json, '{function_name}')\n")
                f.write(f"cat(result)\n")
                script_path = f.name
            
            # Execute R script
            timeout_seconds = (test_case.timeout_ms or 5000) / 1000
            result = subprocess.run(
                [self.r_executable, script_path],
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Parse output
            if result.returncode == 0:
                actual_output = result.stdout.strip()
                expected = json.loads(test_case.expected_output)
                actual = json.loads(actual_output)
                
                passed = self._compare_outputs(expected, actual)
                
                return {
                    'passed': passed,
                    'input': test_case.input_json,
                    'expected_output': test_case.expected_output,
                    'actual_output': actual_output,
                    'error_message': '' if passed else 'Output mismatch',
                    'execution_time_ms': execution_time,
                    'memory_used_mb': 0
                }
            else:
                return {
                    'passed': False,
                    'input': test_case.input_json,
                    'expected_output': test_case.expected_output,
                    'actual_output': '',
                    'error_message': result.stderr,
                    'execution_time_ms': execution_time,
                    'memory_used_mb': 0
                }
                
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'input': test_case.input_json,
                'expected_output': test_case.expected_output,
                'actual_output': '',
                'error_message': 'Execution timeout',
                'execution_time_ms': test_case.timeout_ms or 5000,
                'memory_used_mb': 0
            }
        except Exception as e:
            return {
                'passed': False,
                'input': test_case.input_json,
                'expected_output': test_case.expected_output,
                'actual_output': '',
                'error_message': str(e),
                'execution_time_ms': (time.time() - start_time) * 1000,
                'memory_used_mb': 0
            }
        finally:
            # Clean up temp file
            if os.path.exists(script_path):
                os.unlink(script_path)
    
    def _compare_outputs(self, expected, actual):
        """Compare expected and actual outputs"""
        if type(expected) != type(actual):
            return False
        
        if isinstance(expected, float):
            return abs(expected - actual) < 1e-6
        elif isinstance(expected, (list, tuple)):
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
        return {
            'success': False,
            'all_tests_passed': False,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': [],
            'total_execution_time_ms': 0,
            'errors': [error_message],
            'stdout': '',
            'stderr': ''
        }
    
    def ValidateSyntax(self, request, context):
        """Validate R syntax"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
                f.write(request.code)
                script_path = f.name
            
            result = subprocess.run(
                [self.r_executable, '--vanilla', '-e', f'parse("{script_path}")'],
                capture_output=True,
                text=True
            )
            
            os.unlink(script_path)
            
            if result.returncode == 0:
                return {
                    'is_valid': True,
                    'syntax_errors': [],
                    'warnings': []
                }
            else:
                return {
                    'is_valid': False,
                    'syntax_errors': [result.stderr],
                    'warnings': []
                }
        except Exception as e:
            return {
                'is_valid': False,
                'syntax_errors': [str(e)],
                'warnings': []
            }
    
    def GetLanguageInfo(self, request, context):
        """Get R language information"""
        try:
            result = subprocess.run(
                [self.r_executable, '--version'],
                capture_output=True,
                text=True
            )
            version = result.stdout.split('\n')[0] if result.returncode == 0 else 'Unknown'
        except:
            version = 'Unknown'
        
        return {
            'language': 2,  # R
            'version': version,
            'available_packages': ['dplyr', 'ggplot2', 'tidyr', 'jsonlite'],
            'is_available': self.r_executable is not None
        }

