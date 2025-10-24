"""
Unified gRPC Server - Multi-Language Code Executor and Application Services
Starts all services on different ports
"""

import grpc
from concurrent import futures
import logging
import sys
import os

# Add generated proto files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

# Import generated proto files
import code_executor_pb2
import code_executor_pb2_grpc

# Import service implementations
from app.grpc_services.python_executor import PythonExecutorService
from app.grpc_services.r_executor import RExecutorService
from app.grpc_services.matlab_executor import MatlabExecutorService
from app.grpc_services.application_service import ApplicationServiceImplementation


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serve_code_executors(port=50051):
    """Start unified code executor service for all languages"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register Python executor
    code_executor_pb2_grpc.add_CodeExecutorServiceServicer_to_server(
        PythonExecutorService(), server
    )
    
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"🚀 Code Executor gRPC Server started on port {port}")
    logger.info(f"   - Python Executor: Active")
    logger.info(f"   - R Executor: Active")
    logger.info(f"   - MATLAB Executor: Active")
    return server


def serve_application_service(port=50060):
    """Start application service (replaces FastAPI endpoints)"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register application service
    code_executor_pb2_grpc.add_ApplicationServiceServicer_to_server(
        ApplicationServiceImplementation(), server
    )
    
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"🌐 Application gRPC Server started on port {port}")
    return server


def serve_all():
    """Start all gRPC services"""
    logger.info("=" * 60)
    logger.info("Starting Python Playground gRPC Services...")
    logger.info("=" * 60)
    
    # Start code executor service
    executor_server = serve_code_executors(port=50051)
    
    # Start application service
    app_server = serve_application_service(port=50060)
    
    logger.info("=" * 60)
    logger.info("All services started successfully!")
    logger.info("Press Ctrl+C to stop all services")
    logger.info("=" * 60)
    
    # Keep servers running
    try:
        executor_server.wait_for_termination()
        app_server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
        executor_server.stop(0)
        app_server.stop(0)


if __name__ == '__main__':
    serve_all()
