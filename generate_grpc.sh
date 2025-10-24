#!/bin/bash

# Generate Python gRPC code from proto files

echo "Generating gRPC Python code from proto files..."

# Create output directory if it doesn't exist
mkdir -p app/grpc_services/generated

# Generate Python code
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./app/grpc_services/generated \
    --grpc_python_out=./app/grpc_services/generated \
    ./protos/code_executor.proto

# Create __init__.py to make it a package
touch app/grpc_services/generated/__init__.py

echo "gRPC code generation completed!"
echo "Generated files:"
echo "  - app/grpc_services/generated/code_executor_pb2.py"
echo "  - app/grpc_services/generated/code_executor_pb2_grpc.py"

