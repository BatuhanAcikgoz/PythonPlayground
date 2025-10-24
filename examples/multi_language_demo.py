"""
Example usage of Multi-Language Code Execution Service
Demonstrates how to use the new architecture
"""

from app import create_app
from app.models.base import db
from app.models.programming_question import ProgrammingQuestion
from app.services.code_execution_service import get_code_execution_service


def create_sample_questions():
    """Create sample questions for Python, R, and MATLAB"""
    
    app = create_app()
    with app.app_context():
        
        # Python Question: Fibonacci
        python_q = ProgrammingQuestion(
            title="Fibonacci Sayısı (Python)",
            description="""
Fibonacci dizisinin n. elemanını hesaplayan bir fonksiyon yazın.
Fibonacci dizisi: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...
            """,
            language="python",
            difficulty=2,
            topic="Recursion",
            points=20,
            function_name="fibonacci",
            example_input="5",
            example_output="5",
            test_inputs=json.dumps([[0], [1], [5], [10], [15]]),
            solution_code="""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        )
        
        # R Question: Vector Statistics
        r_q = ProgrammingQuestion(
            title="Vektör İstatistikleri (R)",
            description="""
Bir sayı vektörünün ortalamasını, medyanını ve standart sapmasını hesaplayan
bir fonksiyon yazın. Sonucu liste olarak döndürün.
            """,
            language="r",
            difficulty=1,
            topic="Statistics",
            points=15,
            function_name="vector_stats",
            example_input="c(1, 2, 3, 4, 5)",
            example_output="list(mean=3, median=3, sd=1.58)",
            test_inputs=json.dumps([
                [[1, 2, 3, 4, 5]],
                [[10, 20, 30, 40, 50]]
            ]),
            solution_code="""
vector_stats <- function(vec) {
    result <- list(
        mean = mean(vec),
        median = median(vec),
        sd = sd(vec)
    )
    return(result)
}
"""
        )
        
        # MATLAB Question: Matrix Operations
        matlab_q = ProgrammingQuestion(
            title="Matris İşlemleri (MATLAB)",
            description="""
İki matrisin çarpımını hesaplayan bir fonksiyon yazın.
Matris boyutları uyumlu olmak zorundadır.
            """,
            language="matlab",
            difficulty=2,
            topic="Linear Algebra",
            points=25,
            function_name="matrix_multiply",
            example_input="[1 2; 3 4], [5 6; 7 8]",
            example_output="[19 22; 43 50]",
            test_inputs=json.dumps([
                [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
                [[[1, 0], [0, 1]], [[2, 3], [4, 5]]]
            ]),
            solution_code="""
function result = matrix_multiply(A, B)
    result = A * B;
end
"""
        )
        
        # Add to database
        db.session.add_all([python_q, r_q, matlab_q])
        db.session.commit()
        
        print("✅ Sample questions created!")
        print(f"  - Python: {python_q.id}")
        print(f"  - R: {r_q.id}")
        print(f"  - MATLAB: {matlab_q.id}")


def test_execution_service():
    """Test the multi-language execution service"""
    
    service = get_code_execution_service()
    
    print("\n" + "="*60)
    print("Testing Multi-Language Code Execution")
    print("="*60)
    
    # Test Python
    print("\n🐍 Testing Python...")
    python_result = service.execute_solution(
        language='python',
        code='def add(a, b): return a + b',
        function_name='add',
        test_inputs=json.dumps([[2, 3], [10, 5], [-1, 1]]),
        solution_code='def add(a, b): return a + b'
    )
    print(f"Python Result: {python_result['is_correct']}")
    print(f"Passed: {python_result['passed_tests']}/{python_result['test_count']}")
    
    # Test R
    print("\n📊 Testing R...")
    r_result = service.execute_solution(
        language='r',
        code='add <- function(a, b) { return(a + b) }',
        function_name='add',
        test_inputs=json.dumps([[2, 3], [10, 5]]),
        solution_code='add <- function(a, b) { return(a + b) }'
    )
    print(f"R Result: {r_result['is_correct']}")
    print(f"Passed: {r_result['passed_tests']}/{r_result['test_count']}")
    
    # Test MATLAB
    print("\n🔢 Testing MATLAB...")
    matlab_result = service.execute_solution(
        language='matlab',
        code='function result = add(a, b); result = a + b; end',
        function_name='add',
        test_inputs=json.dumps([[2, 3], [10, 5]]),
        solution_code='function result = add(a, b); result = a + b; end'
    )
    print(f"MATLAB Result: {matlab_result['is_correct']}")
    print(f"Passed: {matlab_result['passed_tests']}/{matlab_result['test_count']}")
    
    print("\n" + "="*60)


def test_syntax_validation():
    """Test syntax validation for different languages"""
    
    service = get_code_execution_service()
    
    print("\n" + "="*60)
    print("Testing Syntax Validation")
    print("="*60)
    
    # Valid Python
    result = service.validate_syntax('python', 'def test(): return 1')
    print(f"\n✅ Valid Python: {result['is_valid']}")
    
    # Invalid Python
    result = service.validate_syntax('python', 'def test( return 1')
    print(f"❌ Invalid Python: {result['is_valid']}")
    if result['syntax_errors']:
        print(f"   Errors: {result['syntax_errors']}")
    
    print("\n" + "="*60)


def demo_starter_code():
    """Demonstrate starter code generation"""
    
    app = create_app()
    with app.app_context():
        service = get_code_execution_service()
        
        # Create a sample question for each language
        questions = {
            'python': ProgrammingQuestion(
                title="Test Python",
                description="A test question",
                language="python",
                function_name="test_func",
                example_input="x",
                example_output="y",
                difficulty=1,
                topic="Test",
                points=10
            ),
            'r': ProgrammingQuestion(
                title="Test R",
                description="A test question",
                language="r",
                function_name="test_func",
                example_input="x",
                example_output="y",
                difficulty=1,
                topic="Test",
                points=10
            ),
            'matlab': ProgrammingQuestion(
                title="Test MATLAB",
                description="A test question",
                language="matlab",
                function_name="test_func",
                example_input="x",
                example_output="y",
                difficulty=1,
                topic="Test",
                points=10
            )
        }
        
        print("\n" + "="*60)
        print("Starter Code Templates")
        print("="*60)
        
        for lang, question in questions.items():
            print(f"\n{lang.upper()} Template:")
            print("-" * 40)
            print(service.get_starter_code(question))


if __name__ == '__main__':
    # Uncomment the functions you want to run
    
    # create_sample_questions()
    # test_execution_service()
    # test_syntax_validation()
    # demo_starter_code()
    
    print("\n" + "="*60)
    print("🎉 Multi-Language Code Execution Demo")
    print("="*60)
    print("\nUncomment the functions in __main__ to run demos:")
    print("  - create_sample_questions()")
    print("  - test_execution_service()")
    print("  - test_syntax_validation()")
    print("  - demo_starter_code()")
    print("="*60 + "\n")
"""
Test Multi-Language Code Execution Services
"""

import pytest
import json
from app.grpc_services import CodeExecutorClient
from app.grpc_services import PythonExecutorService
from app.grpc_services import RExecutorService
from app.grpc_services import MatlabExecutorService


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
    
    def test_language_info(self):
        """Test getting language information"""
        client = CodeExecutorClient()
        
        info = client.get_language_info('python')
        
        assert info['is_available'] == True
        assert 'version' in info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

