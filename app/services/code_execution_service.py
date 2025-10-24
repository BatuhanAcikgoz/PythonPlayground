"""
Code Execution Service
Multi-language code execution service using gRPC executors
"""

import json
from typing import Dict, List, Any, Optional
from app.grpc_services import get_executor_client


class CodeExecutionService:
    """
    Service layer for executing code in multiple languages
    Uses gRPC-based executor services for language-agnostic execution
    """

    def __init__(self):
        self.executor_client = get_executor_client()

    def execute_solution(
        self,
        language: str,
        code: str,
        function_name: str,
        test_inputs: str,
        solution_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute user code against test cases

        Args:
            language: Programming language ('python', 'r', 'matlab')
            code: User's code to execute
            function_name: Name of the function to test
            test_inputs: JSON string of test cases
            solution_code: Reference solution code (optional)

        Returns:
            Dictionary with execution results:
            {
                'is_correct': bool,
                'execution_time': float,
                'test_count': int,
                'passed_tests': int,
                'failed_tests': int,
                'test_results': list,
                'error_message': list
            }
        """
        try:
            # Parse test inputs
            test_data = json.loads(test_inputs)

            # Generate expected outputs using solution code if provided
            test_cases = []
            if solution_code:
                expected_outputs = self._get_expected_outputs(
                    language, solution_code, function_name, test_data
                )
                for test_input, expected_output in zip(test_data, expected_outputs):
                    test_cases.append({
                        'input': test_input,
                        'expected_output': expected_output,
                        'timeout_ms': 5000
                    })
            else:
                # If no solution code, test inputs should include expected outputs
                for test_case in test_data:
                    if isinstance(test_case, dict) and 'input' in test_case:
                        test_cases.append(test_case)
                    else:
                        raise ValueError("Test cases must include expected outputs")

            # Execute code via gRPC executor
            result = self.executor_client.execute_code(
                language=language,
                code=code,
                function_name=function_name,
                test_cases=test_cases,
                solution_code=solution_code
            )

            # Format response
            return {
                'is_correct': result.get('all_tests_passed', False),
                'execution_time': result.get('total_execution_time_ms', 0),
                'test_count': result.get('total_tests', 0),
                'passed_tests': result.get('passed_tests', 0),
                'failed_tests': result.get('failed_tests', 0),
                'test_results': result.get('test_results', []),
                'error_message': result.get('errors', [])
            }

        except json.JSONDecodeError as e:
            return self._error_response(f"Invalid test input JSON: {str(e)}")
        except Exception as e:
            return self._error_response(f"Execution error: {str(e)}")

    def _get_expected_outputs(
        self,
        language: str,
        solution_code: str,
        function_name: str,
        test_inputs: List[Any]
    ) -> List[Any]:
        """
        Execute solution code to get expected outputs

        Args:
            language: Programming language
            solution_code: Reference solution code
            function_name: Function name
            test_inputs: List of test inputs

        Returns:
            List of expected outputs
        """
        # Create temporary test cases with dummy expected outputs
        temp_test_cases = [{
            'input': test_input,
            'expected_output': None,  # Will be replaced
            'timeout_ms': 5000
        } for test_input in test_inputs]

        # Execute solution code
        result = self.executor_client.execute_code(
            language=language,
            code=solution_code,
            function_name=function_name,
            test_cases=temp_test_cases
        )

        # Extract actual outputs as expected outputs
        expected_outputs = []
        for test_result in result.get('test_results', []):
            try:
                output = json.loads(test_result['actual_output'])
                expected_outputs.append(output)
            except:
                expected_outputs.append(test_result['actual_output'])

        return expected_outputs

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
            result = self.executor_client.validate_syntax(language, code)
            return result
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
            return self.executor_client.get_language_info(language)
        except Exception as e:
            return {
                'language': language,
                'version': 'Unknown',
                'available_packages': [],
                'is_available': False,
                'error': str(e)
            }

    def get_starter_code(self, question) -> str:
        """
        Generate starter code template for a question based on language

        Args:
            question: ProgrammingQuestion model instance

        Returns:
            String containing starter code template
        """
        language = question.language.lower()

        if language == 'python':
            return self._generate_python_starter(question)
        elif language == 'r':
            return self._generate_r_starter(question)
        elif language == 'matlab':
            return self._generate_matlab_starter(question)
        else:
            return f"# {question.title}\n# TODO: Implement {question.function_name}\n"

    def _generate_python_starter(self, question) -> str:
        """Generate Python starter code"""
        return f'''def {question.function_name}():
    """
    {question.title}
    
    {question.description[:100]}...
    
    Example:
    Input: {question.example_input}
    Output: {question.example_output}
    """
    # Your code here
    pass
'''

    def _generate_r_starter(self, question) -> str:
        """Generate R starter code"""
        return f'''# {question.title}
# {question.description[:100]}...
#
# Example:
# Input: {question.example_input}
# Output: {question.example_output}

{question.function_name} <- function() {{
    # Your code here
}}
'''

    def _generate_matlab_starter(self, question) -> str:
        """Generate MATLAB starter code"""
        return f'''% {question.title}
% {question.description[:100]}...
%
% Example:
% Input: {question.example_input}
% Output: {question.example_output}

function result = {question.function_name}()
    % Your code here
end
'''

    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'is_correct': False,
            'execution_time': 0,
            'test_count': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': [],
            'error_message': [error_message]
        }


# Global service instance
_code_execution_service = None


def get_code_execution_service() -> CodeExecutionService:
    """Get or create global code execution service"""
    global _code_execution_service
    if _code_execution_service is None:
        _code_execution_service = CodeExecutionService()
    return _code_execution_service

