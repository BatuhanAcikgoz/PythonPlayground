"""
gRPC Client for Code Execution Services
Provides unified interface to execute code in different languages
"""

import grpc
import json
import sys
import os
from typing import Dict, List, Any, Optional

# Add generated proto files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

# Import generated proto files
import code_executor_pb2
import code_executor_pb2_grpc


class CodeExecutorClient:
    """
    Client for communicating with language-specific executor services via gRPC
    """
    
    def __init__(self, service_config: Optional[Dict[str, str]] = None):
        """
        Initialize executor client
        
        Args:
            service_config: Dictionary mapping language to gRPC server address
                Example: {
                    'python': 'localhost:50051',
                    'r': 'localhost:50052',
                    'matlab': 'localhost:50053'
                }
        """
        self.service_config = service_config or {
            'python': 'localhost:50051',
            'r': 'localhost:50051',  # All use same port now
            'matlab': 'localhost:50051'
        }
        self.channels = {}
        self.stubs = {}
    
    def _get_stub(self, language: str):
        """Get or create gRPC stub for language"""
        if language not in self.stubs:
            address = self.service_config.get(language.lower())
            if not address:
                raise ValueError(f"No service configured for language: {language}")
            
            # Create channel
            channel = grpc.insecure_channel(address)
            self.channels[language] = channel

            # Create stub
            self.stubs[language] = code_executor_pb2_grpc.CodeExecutorServiceStub(channel)

        return self.stubs[language]

    def execute_code(
        self,
        language: str,
        code: str,
        function_name: str,
        test_cases: List[Dict[str, Any]],
        solution_code: Optional[str] = None,
        memory_limit_mb: int = 256,
        cpu_limit_percent: int = 50
    ) -> Dict[str, Any]:
        """
        Execute code in specified language via gRPC

        Args:
            language: Programming language ('python', 'r', 'matlab')
            code: User's code to execute
            function_name: Name of the function to test
            test_cases: List of test cases, each with 'input' and 'expected_output'
            solution_code: Reference solution (optional)
            memory_limit_mb: Memory limit in MB
            cpu_limit_percent: CPU usage limit percentage
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Get gRPC stub
            stub = self._get_stub(language)

            # Map language to proto enum
            language_enum = self._language_to_enum(language)

            # Prepare test cases for proto
            proto_test_cases = []
            for test in test_cases:
                proto_test_cases.append(
                    code_executor_pb2.TestCase(
                        input_json=json.dumps(test['input']),
                        expected_output=json.dumps(test.get('expected_output', '')),
                        timeout_ms=test.get('timeout_ms', 5000)
                    )
                )

            # Create request
            request = code_executor_pb2.ExecutionRequest(
                language=language_enum,
                code=code,
                function_name=function_name,
                test_cases=proto_test_cases,
                solution_code=solution_code or '',
                memory_limit_mb=memory_limit_mb,
                cpu_limit_percent=cpu_limit_percent
            )

            # Call gRPC service
            response = stub.ExecuteCode(request)

            # Convert proto response to dict
            return self._proto_response_to_dict(response)

        except grpc.RpcError as e:
            return {
                'success': False,
                'all_tests_passed': False,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'test_results': [],
                'total_execution_time_ms': 0,
                'errors': [f"gRPC Error: {e.details()}"],
                'stdout': '',
                'stderr': ''
            }
        except Exception as e:
            return {
                'success': False,
                'all_tests_passed': False,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'test_results': [],
                'total_execution_time_ms': 0,
                'errors': [f"Client Error: {str(e)}"],
                'stdout': '',
                'stderr': ''
            }

    def validate_syntax(self, language: str, code: str) -> Dict[str, Any]:
        """
        Validate code syntax without execution
        
        Args:
            language: Programming language
            code: Code to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            stub = self._get_stub(language)
            language_enum = self._language_to_enum(language)

            request = code_executor_pb2.ValidationRequest(
                language=language_enum,
                code=code
            )

            response = stub.ValidateSyntax(request)

            return {
                'is_valid': response.is_valid,
                'syntax_errors': list(response.syntax_errors),
                'warnings': list(response.warnings)
            }
        except Exception as e:
            return {
                'is_valid': False,
                'syntax_errors': [str(e)],
                'warnings': []
            }

    def get_language_info(self, language: str) -> Dict[str, Any]:
        """
        Get information about language runtime
        
        Args:
            language: Programming language
            
        Returns:
            Dictionary with language information
        """
        try:
            stub = self._get_stub(language)
            language_enum = self._language_to_enum(language)

            request = code_executor_pb2.LanguageInfoRequest(
                language=language_enum
            )

            response = stub.GetLanguageInfo(request)

            return {
                'language': self._enum_to_language(response.language),
                'version': response.version,
                'available_packages': list(response.available_packages),
                'is_available': response.is_available
            }
        except Exception as e:
            return {
                'language': language,
                'version': 'Unknown',
                'available_packages': [],
                'is_available': False,
                'error': str(e)
            }

    def _language_to_enum(self, language: str):
        """Convert language string to proto enum"""
        language_map = {
            'python': code_executor_pb2.PYTHON,
            'r': code_executor_pb2.R,
            'matlab': code_executor_pb2.MATLAB
        }
        return language_map.get(language.lower(), code_executor_pb2.PYTHON)

    def _enum_to_language(self, enum_value):
        """Convert proto enum to language string"""
        enum_map = {
            code_executor_pb2.PYTHON: 'python',
            code_executor_pb2.R: 'r',
            code_executor_pb2.MATLAB: 'matlab'
        }
        return enum_map.get(enum_value, 'python')

    def _proto_response_to_dict(self, response):
        """Convert proto ExecutionResponse to dictionary"""
        test_results = []
        for test_result in response.test_results:
            test_results.append({
                'passed': test_result.passed,
                'input': test_result.input,
                'expected_output': test_result.expected_output,
                'actual_output': test_result.actual_output,
                'error_message': test_result.error_message,
                'execution_time_ms': test_result.execution_time_ms,
                'memory_used_mb': test_result.memory_used_mb
            })

        return {
            'success': response.success,
            'all_tests_passed': response.all_tests_passed,
            'total_tests': response.total_tests,
            'passed_tests': response.passed_tests,
            'failed_tests': response.failed_tests,
            'test_results': test_results,
            'total_execution_time_ms': response.total_execution_time_ms,
            'errors': list(response.errors),
            'stdout': response.stdout,
            'stderr': response.stderr
        }

    def close(self):
        """Close all gRPC channels"""
        for channel in self.channels.values():
            channel.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global client instance
_executor_client = None


def get_executor_client() -> CodeExecutorClient:
    """Get or create global executor client"""
    global _executor_client
    if _executor_client is None:
        _executor_client = CodeExecutorClient()
    return _executor_client
