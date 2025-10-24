#!/usr/bin/env python3
"""
Start all gRPC services with HTTP/JSON Gateway
"""

import os
import sys
import time
import logging
import threading
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def start_grpc_servers():
    """Start gRPC servers in background"""
    logger.info("🚀 Starting gRPC servers...")
    
    # Start gRPC server
    grpc_process = subprocess.Popen(
        [sys.executable, '-m', 'app.grpc_services.server'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait a bit for servers to start
    time.sleep(3)
    
    return grpc_process


def start_http_gateway():
    """Start HTTP/JSON Gateway"""
    logger.info("🌉 Starting HTTP/JSON Gateway...")
    
    from app.grpc_services.grpc_http_gateway import start_gateway
    
    # Start gateway (blocking)
    start_gateway(host='0.0.0.0', port=8080)


def main():
    """Main entry point"""
    logger.info("=" * 70)
    logger.info("🎯 Python Playground - gRPC Services with HTTP/JSON Gateway")
    logger.info("=" * 70)
    
    try:
        # Start gRPC servers
        grpc_process = start_grpc_servers()
        
        # Start HTTP gateway (blocking)
        start_http_gateway()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutting down services...")
        if grpc_process:
            grpc_process.terminate()
            grpc_process.wait()
        logger.info("✅ All services stopped")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

