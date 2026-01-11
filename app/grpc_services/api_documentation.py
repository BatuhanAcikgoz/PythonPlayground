"""
Automatic API Documentation Generator for gRPC Services
Auto-generates OpenAPI/Swagger documentation from protobuf definitions
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class ParameterInfo:
    name: str
    type: str
    required: bool = True
    description: str = ""
    in_: str = "body"  # body, query, path
    
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "description": self.description,
            "in": self.in_
        }


@dataclass
class EndpointInfo:
    path: str
    method: HTTPMethod
    service: str
    rpc_method: str
    summary: str
    description: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    parameters: List[ParameterInfo]
    
    def to_dict(self):
        return {
            "path": self.path,
            "method": self.method.value,
            "service": self.service,
            "rpc_method": self.rpc_method,
            "summary": self.summary,
            "description": self.description,
            "request_schema": self.request_schema,
            "response_schema": self.response_schema,
            "parameters": [p.to_dict() for p in self.parameters]
        }


class APIDocumentationGenerator:
    """Generate OpenAPI documentation from protobuf definitions"""

    def __init__(self, proto_file_path: str = None):
        self.endpoints: List[EndpointInfo] = []

        # Default proto file location
        if proto_file_path is None:
            proto_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'protos',
                'code_executor.proto'
            )

        # Auto-generate from proto file
        self._auto_generate_from_proto(proto_file_path)

    def _auto_generate_from_proto(self, proto_file_path: str):
        """Auto-generate documentation from proto file"""
        from app.grpc_services.proto_parser import APIDocGenerator

        doc_gen = APIDocGenerator(proto_file_path)
        openapi_spec = doc_gen.generate_openapi_spec()

        # Convert OpenAPI spec to endpoints
        self._convert_openapi_to_endpoints(openapi_spec)

    def _convert_openapi_to_endpoints(self, openapi_spec: Dict):
        """Convert OpenAPI spec to endpoint list"""
        # Store the full OpenAPI spec for later use
        self._openapi_spec = openapi_spec

        for path, methods in openapi_spec.get('paths', {}).items():
            for method, operation in methods.items():
                # Extract request/response schemas
                request_schema = {}
                response_schema = {}
                parameters = []

                # Get request schema
                if 'requestBody' in operation:
                    req_ref = operation['requestBody']['content']['application/json']['schema'].get('$ref')
                    if req_ref:
                        schema_name = req_ref.split('/')[-1]
                        request_schema = openapi_spec['components']['schemas'].get(schema_name, {}).get('properties', {})

                # Get response schema
                if '200' in operation['responses']:
                    resp_ref = operation['responses']['200']['content']['application/json']['schema'].get('$ref')
                    if resp_ref:
                        schema_name = resp_ref.split('/')[-1]
                        response_schema = openapi_spec['components']['schemas'].get(schema_name, {}).get('properties', {})

                # Get parameters
                if 'parameters' in operation:
                    for param in operation['parameters']:
                        parameters.append(ParameterInfo(
                            name=param['name'],
                            type=param['schema'].get('type', 'string'),
                            required=param.get('required', False),
                            description=param.get('description', ''),
                            in_=param['in']
                        ))

                # Extract service and RPC method
                service = operation['tags'][0] if 'tags' in operation else 'Unknown'
                rpc_method = operation.get('summary', '').replace(' ', '')

                endpoint = EndpointInfo(
                    path=path,
                    method=HTTPMethod[method.upper()],
                    service=service,
                    rpc_method=rpc_method,
                    summary=operation.get('summary', ''),
                    description=operation.get('description', ''),
                    request_schema=request_schema,
                    response_schema=response_schema,
                    parameters=parameters
                )
                self.endpoints.append(endpoint)

    def get_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Python Playground gRPC API",
                "version": "1.0.0",
                "description": "Auto-generated from protobuf - Multi-language code execution platform",
                "contact": {
                    "name": "API Support",
                    "url": "https://github.com/your-repo"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8080",
                    "description": "Development server"
                }
            ],
            "paths": self._generate_paths(),
            "components": {
                "schemas": self._generate_schemas()
            }
        }
    
    def _generate_paths(self) -> Dict[str, Any]:
        """Generate paths section of OpenAPI spec"""
        paths = {}
        
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            method_lower = endpoint.method.value.lower()
            paths[endpoint.path][method_lower] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": [endpoint.service],
                "parameters": [p.to_dict() for p in endpoint.parameters],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "500": {
                        "description": "Server error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                        "code": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if endpoint.request_schema:
                paths[endpoint.path][method_lower]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
        
        return paths
    
    def _generate_schemas(self) -> Dict[str, Any]:
        """Generate reusable schemas from proto messages"""
        # If we have the full OpenAPI spec from proto parser, use its schemas
        if hasattr(self, '_openapi_spec') and 'components' in self._openapi_spec:
            return self._openapi_spec['components'].get('schemas', {})

        # Fallback: just error schema
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "code": {"type": "string"}
                }
            }
        }
    
    def get_endpoints_list(self) -> List[Dict[str, Any]]:
        """Get simplified list of all endpoints"""
        return [e.to_dict() for e in self.endpoints]
