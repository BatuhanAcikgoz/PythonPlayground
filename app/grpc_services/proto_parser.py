"""
Proto File Parser - Automatically extract API documentation from .proto files
Parses protobuf definitions and generates API documentation automatically
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ProtoField:
    """Represents a field in a proto message"""
    name: str
    type: str
    number: int
    repeated: bool = False
    description: str = ""


@dataclass
class ProtoMessage:
    """Represents a proto message definition"""
    name: str
    fields: List[ProtoField] = field(default_factory=list)
    description: str = ""


@dataclass
class ProtoRPC:
    """Represents an RPC method"""
    name: str
    request_type: str
    response_type: str
    description: str = ""


@dataclass
class ProtoService:
    """Represents a proto service"""
    name: str
    rpcs: List[ProtoRPC] = field(default_factory=list)
    description: str = ""


class ProtoParser:
    """Parse .proto files and extract API information"""
    
    def __init__(self, proto_file_path: str):
        self.proto_file_path = Path(proto_file_path)
        self.services: List[ProtoService] = []
        self.messages: Dict[str, ProtoMessage] = {}
        self.enums: Dict[str, List[str]] = {}
        
    def parse(self):
        """Parse the proto file"""
        with open(self.proto_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comments but keep documentation comments
        content = self._preserve_doc_comments(content)
        
        # Parse services
        self._parse_services(content)
        
        # Parse messages
        self._parse_messages(content)
        
        # Parse enums
        self._parse_enums(content)
    
    def _preserve_doc_comments(self, content: str) -> str:
        """Extract documentation comments"""
        # Store doc comments with special markers
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Keep lines that start with //
            if line.strip().startswith('//'):
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _parse_services(self, content: str):
        """Parse service definitions"""
        # Match service blocks
        service_pattern = r'service\s+(\w+)\s*\{([^}]+)\}'
        
        for match in re.finditer(service_pattern, content, re.MULTILINE | re.DOTALL):
            service_name = match.group(1)
            service_body = match.group(2)
            
            # Get service description from comments above
            service_desc = self._get_description_before(content, match.start())
            
            service = ProtoService(name=service_name, description=service_desc)
            
            # Parse RPCs
            rpc_pattern = r'rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)'
            
            for rpc_match in re.finditer(rpc_pattern, service_body):
                rpc_name = rpc_match.group(1)
                request_type = rpc_match.group(2)
                response_type = rpc_match.group(3)
                
                # Get RPC description
                rpc_desc = self._get_description_before(service_body, rpc_match.start())
                
                rpc = ProtoRPC(
                    name=rpc_name,
                    request_type=request_type,
                    response_type=response_type,
                    description=rpc_desc
                )
                service.rpcs.append(rpc)
            
            self.services.append(service)
    
    def _parse_messages(self, content: str):
        """Parse message definitions"""
        # Match message blocks
        message_pattern = r'message\s+(\w+)\s*\{([^}]+)\}'
        
        for match in re.finditer(message_pattern, content, re.MULTILINE | re.DOTALL):
            message_name = match.group(1)
            message_body = match.group(2)
            
            # Get message description
            msg_desc = self._get_description_before(content, match.start())
            
            message = ProtoMessage(name=message_name, description=msg_desc)
            
            # Parse fields
            field_pattern = r'(repeated\s+)?(\w+)\s+(\w+)\s*=\s*(\d+);'
            
            for field_match in re.finditer(field_pattern, message_body):
                is_repeated = bool(field_match.group(1))
                field_type = field_match.group(2)
                field_name = field_match.group(3)
                field_number = int(field_match.group(4))
                
                # Get field description
                field_desc = self._get_description_before(message_body, field_match.start())
                
                field = ProtoField(
                    name=field_name,
                    type=field_type,
                    number=field_number,
                    repeated=is_repeated,
                    description=field_desc
                )
                message.fields.append(field)
            
            self.messages[message_name] = message
    
    def _parse_enums(self, content: str):
        """Parse enum definitions"""
        enum_pattern = r'enum\s+(\w+)\s*\{([^}]+)\}'
        
        for match in re.finditer(enum_pattern, content, re.MULTILINE | re.DOTALL):
            enum_name = match.group(1)
            enum_body = match.group(2)
            
            values = []
            value_pattern = r'(\w+)\s*=\s*(\d+);'
            
            for value_match in re.finditer(value_pattern, enum_body):
                value_name = value_match.group(1)
                values.append(value_name)
            
            self.enums[enum_name] = values
    
    def _get_description_before(self, content: str, position: int) -> str:
        """Extract comment before a position"""
        # Get text before position
        before_text = content[:position]
        lines = before_text.split('\n')
        
        # Get last few lines
        description_lines = []
        for line in reversed(lines[-10:]):
            stripped = line.strip()
            if stripped.startswith('//'):
                # Remove // and clean
                desc = stripped[2:].strip()
                description_lines.insert(0, desc)
            elif stripped == '':
                continue
            else:
                break
        
        return ' '.join(description_lines) if description_lines else ''
    
    def get_message_schema(self, message_name: str) -> Dict[str, Any]:
        """Convert a proto message to JSON schema"""
        if message_name not in self.messages:
            return {}
        
        message = self.messages[message_name]
        schema = {}
        
        for field in message.fields:
            field_schema = self._field_to_schema(field)
            schema[field.name] = field_schema
        
        return schema
    
    def _field_to_schema(self, field: ProtoField) -> Dict[str, Any]:
        """Convert a proto field to JSON schema"""
        type_mapping = {
            'string': 'string',
            'int32': 'integer',
            'int64': 'integer',
            'uint32': 'integer',
            'uint64': 'integer',
            'bool': 'boolean',
            'double': 'number',
            'float': 'number',
            'bytes': 'string'
        }
        
        base_type = type_mapping.get(field.type, 'object')
        
        schema = {'type': base_type}
        
        if field.description:
            schema['description'] = field.description
        
        if field.repeated:
            schema = {
                'type': 'array',
                'items': {'type': base_type}
            }
        
        # Handle enum types
        if field.type in self.enums:
            enum_values = list(range(len(self.enums[field.type])))
            schema['enum'] = enum_values
            schema['description'] = (schema.get('description', '') + 
                                   f" Enum: {', '.join(f'{i}={v}' for i, v in enumerate(self.enums[field.type]))}")
        
        # Handle nested message types
        if field.type in self.messages:
            nested_schema = self.get_message_schema(field.type)
            if field.repeated:
                schema = {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': nested_schema
                    }
                }
            else:
                schema = {
                    'type': 'object',
                    'properties': nested_schema
                }
        
        return schema


class APIDocGenerator:
    """Generate API documentation from proto files"""
    
    # HTTP endpoint mapping rules
    ENDPOINT_MAPPINGS = {
        # Service: CodeExecutorService
        'ExecuteCode': {'path': '/api/v1/executor/execute', 'method': 'POST'},
        'ValidateSyntax': {'path': '/api/v1/executor/validate', 'method': 'POST'},
        'GetLanguageInfo': {'path': '/api/v1/executor/language-info', 'method': 'POST'},
        
        # Service: ApplicationService
        'GetServerStatus': {'path': '/api/v1/status', 'method': 'GET'},
        'HealthCheck': {'path': '/api/v1/health', 'method': 'GET'},
        'GetRecentUsers': {'path': '/api/v1/users/recent', 'method': 'GET'},
        'GetUserProfile': {'path': '/api/v1/users/{username}/profile', 'method': 'GET'},
        'GetLastQuestionsDetail': {'path': '/api/v1/last-questions-detail', 'method': 'GET'},
        'GenerateQuestion': {'path': '/api/v1/questions/generate', 'method': 'POST'},
        'SaveQuestion': {'path': '/api/v1/questions/save', 'method': 'POST'},
        'GetLastSubmissions': {'path': '/api/v1/submissions/recent', 'method': 'GET'},
        'GetLeaderboard': {'path': '/api/v1/leaderboard', 'method': 'GET'},
        'GetRegistrationChart': {'path': '/api/v1/charts/registrations', 'method': 'GET'},
        'GetSolvedQuestionsChart': {'path': '/api/v1/charts/solved-questions', 'method': 'GET'},
        'GetActivityStats': {'path': '/api/v1/charts/activity', 'method': 'GET'},
        'ProcessNotebookSummary': {'path': '/api/v1/notebook/summary', 'method': 'POST'},
        'TriggerEvent': {'path': '/api/v1/events/trigger', 'method': 'POST'},
        'GetInstagramPosts': {'path': '/api/v1/instagram-posts', 'method': 'GET'},
        'RefreshInstagramCache': {'path': '/api/v1/instagram/refresh', 'method': 'POST'},
        'ProxyImage': {'path': '/api/v1/proxy-image', 'method': 'GET'},
    }
    
    def __init__(self, proto_file_path: str):
        self.parser = ProtoParser(proto_file_path)
        self.parser.parse()
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Python Playground gRPC API",
                "version": "1.0.0",
                "description": "Auto-generated from protobuf definitions - Multi-language code execution platform",
            },
            "servers": [
                {"url": "http://localhost:8080", "description": "Development server"}
            ],
            "paths": {},
            "components": {
                "schemas": self._generate_schemas()
            }
        }
        
        # Generate paths from services
        for service in self.parser.services:
            for rpc in service.rpcs:
                endpoint_info = self.ENDPOINT_MAPPINGS.get(rpc.name)
                if endpoint_info:
                    path = endpoint_info['path']
                    method = endpoint_info['method'].lower()
                    
                    if path not in spec['paths']:
                        spec['paths'][path] = {}
                    
                    spec['paths'][path][method] = self._generate_operation(service, rpc)
        
        return spec
    
    def _generate_schemas(self) -> Dict[str, Any]:
        """Generate component schemas from proto messages"""
        schemas = {}
        
        for msg_name, message in self.parser.messages.items():
            schema = {
                "type": "object",
                "properties": {}
            }
            
            if message.description:
                schema['description'] = message.description
            
            for field in message.fields:
                schema['properties'][field.name] = self.parser._field_to_schema(field)
            
            schemas[msg_name] = schema
        
        return schemas
    
    def _generate_operation(self, service: ProtoService, rpc: ProtoRPC) -> Dict[str, Any]:
        """Generate OpenAPI operation for an RPC"""
        operation = {
            "summary": self._format_rpc_name(rpc.name),
            "description": rpc.description or f"{rpc.name} endpoint from {service.name}",
            "tags": [service.name],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{rpc.response_type}"}
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
        
        # Add request body for POST methods
        endpoint_info = self.ENDPOINT_MAPPINGS.get(rpc.name, {})
        if endpoint_info.get('method') == 'POST' and rpc.request_type != 'Empty':
            operation['requestBody'] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{rpc.request_type}"}
                    }
                }
            }
        
        # Add query parameters for GET methods with request params
        if endpoint_info.get('method') == 'GET' and rpc.request_type in self.parser.messages:
            request_msg = self.parser.messages[rpc.request_type]
            if request_msg.fields:
                operation['parameters'] = []
                for field in request_msg.fields:
                    param = {
                        "name": field.name,
                        "in": "query",
                        "required": False,
                        "schema": self.parser._field_to_schema(field)
                    }
                    if field.description:
                        param['description'] = field.description
                    operation['parameters'].append(param)
        
        return operation
    
    def _format_rpc_name(self, name: str) -> str:
        """Format RPC name to human-readable"""
        # Convert CamelCase to Title Case with spaces
        result = re.sub('([A-Z])', r' \1', name).strip()
        return result
    
    def generate_markdown_docs(self) -> str:
        """Generate markdown documentation"""
        docs = ["# API Documentation\n\n"]
        docs.append("Auto-generated from protobuf definitions.\n\n")
        
        for service in self.parser.services:
            docs.append(f"## {service.name}\n\n")
            if service.description:
                docs.append(f"{service.description}\n\n")
            
            for rpc in service.rpcs:
                endpoint_info = self.ENDPOINT_MAPPINGS.get(rpc.name)
                if endpoint_info:
                    method = endpoint_info['method']
                    path = endpoint_info['path']
                    docs.append(f"### {method} `{path}`\n\n")
                    
                    if rpc.description:
                        docs.append(f"{rpc.description}\n\n")
                    
                    docs.append(f"**Request:** `{rpc.request_type}`\n\n")
                    docs.append(f"**Response:** `{rpc.response_type}`\n\n")
                    
                    # Add request schema
                    if rpc.request_type in self.parser.messages:
                        docs.append("**Request Fields:**\n\n")
                        request_msg = self.parser.messages[rpc.request_type]
                        for field in request_msg.fields:
                            docs.append(f"- `{field.name}` ({field.type})")
                            if field.description:
                                docs.append(f": {field.description}")
                            docs.append("\n")
                        docs.append("\n")
        
        return ''.join(docs)

