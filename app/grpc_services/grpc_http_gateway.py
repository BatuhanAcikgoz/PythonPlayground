"""
gRPC-HTTP Gateway - JSON REST API Bridge for gRPC Services
Converts HTTP/JSON requests to gRPC calls and vice versa
"""

import grpc
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add generated proto files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

import code_executor_pb2
import code_executor_pb2_grpc

from google.protobuf.json_format import MessageToDict, Parse, ParseError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrpcHttpGateway:
    """HTTP to gRPC Gateway for all services"""
    
    def __init__(self, grpc_executor_host='localhost:50051', grpc_app_host='localhost:50060'):
        self.grpc_executor_host = grpc_executor_host
        self.grpc_app_host = grpc_app_host
        
        # Create gRPC channels
        self.executor_channel = grpc.insecure_channel(grpc_executor_host)
        self.app_channel = grpc.insecure_channel(grpc_app_host)
        
        # Create stubs
        self.executor_stub = code_executor_pb2_grpc.CodeExecutorServiceStub(self.executor_channel)
        self.app_stub = code_executor_pb2_grpc.ApplicationServiceStub(self.app_channel)
        
        logger.info(f"✅ Connected to Code Executor gRPC: {grpc_executor_host}")
        logger.info(f"✅ Connected to Application gRPC: {grpc_app_host}")
    
    def __del__(self):
        """Close channels on cleanup"""
        try:
            self.executor_channel.close()
            self.app_channel.close()
        except:
            pass


# Create Flask app for HTTP gateway
gateway_app = Flask(__name__)
CORS(gateway_app)

# Global gateway instance
gateway = None


def init_gateway():
    """Initialize the gateway"""
    global gateway
    if gateway is None:
        gateway = GrpcHttpGateway()
    return gateway


# =============================================================================
# CODE EXECUTOR ENDPOINTS
# =============================================================================

@gateway_app.route('/api/v1/executor/execute', methods=['POST'])
def execute_code():
    """Execute code with test cases"""
    try:
        gw = init_gateway()
        data = request.get_json()
        
        # Convert JSON to protobuf message
        grpc_request = Parse(json.dumps(data), code_executor_pb2.ExecutionRequest())
        
        # Call gRPC service
        response = gw.executor_stub.ExecuteCode(grpc_request)
        
        # Convert protobuf response to JSON
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.code()} - {e.details()}")
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except ParseError as e:
        logger.error(f"JSON parse error: {str(e)}")
        return jsonify({"error": f"Invalid request format: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/executor/validate', methods=['POST'])
def validate_syntax():
    """Validate code syntax"""
    try:
        gw = init_gateway()
        data = request.get_json()
        
        grpc_request = Parse(json.dumps(data), code_executor_pb2.ValidationRequest())
        response = gw.executor_stub.ValidateSyntax(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/executor/language-info', methods=['POST'])
def get_language_info():
    """Get language runtime information"""
    try:
        gw = init_gateway()
        data = request.get_json()
        
        grpc_request = Parse(json.dumps(data), code_executor_pb2.LanguageInfoRequest())
        response = gw.executor_stub.GetLanguageInfo(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# APPLICATION SERVICE ENDPOINTS
# =============================================================================

@gateway_app.route('/api/v1/status', methods=['GET'])
def get_server_status():
    """Get server status"""
    try:
        gw = init_gateway()
        grpc_request = code_executor_pb2.Empty()
        response = gw.app_stub.GetServerStatus(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        gw = init_gateway()
        grpc_request = code_executor_pb2.Empty()
        response = gw.app_stub.HealthCheck(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/users/recent', methods=['GET'])
def get_recent_users():
    """Get recent users"""
    try:
        gw = init_gateway()
        limit = request.args.get('limit', 10, type=int)
        
        grpc_request = code_executor_pb2.RecentUsersRequest(limit=limit)
        response = gw.app_stub.GetRecentUsers(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/users/<username>/profile', methods=['GET'])
def get_user_profile(username):
    """Get user profile"""
    try:
        gw = init_gateway()
        grpc_request = code_executor_pb2.UserProfileRequest(username=username)
        response = gw.app_stub.GetUserProfile(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/questions/recent', methods=['GET'])
def get_recent_questions():
    """Get recent questions"""
    try:
        gw = init_gateway()
        limit = request.args.get('limit', 10, type=int)
        
        grpc_request = code_executor_pb2.LastQuestionsRequest(limit=limit)
        response = gw.app_stub.GetLastQuestionsDetail(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/questions/generate', methods=['POST'])
def generate_question():
    """Generate AI question"""
    try:
        gw = init_gateway()
        data = request.get_json()
        
        grpc_request = Parse(json.dumps(data), code_executor_pb2.GenerateQuestionRequest())
        response = gw.app_stub.GenerateQuestion(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/questions/save', methods=['POST'])
def save_question():
    """Save question"""
    try:
        gw = init_gateway()
        data = request.get_json()
        
        grpc_request = Parse(json.dumps(data), code_executor_pb2.SaveQuestionRequest())
        response = gw.app_stub.SaveQuestion(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/submissions/recent', methods=['GET'])
def get_recent_submissions():
    """Get recent submissions"""
    try:
        gw = init_gateway()
        limit = request.args.get('limit', 10, type=int)
        
        grpc_request = code_executor_pb2.LastSubmissionsRequest(limit=limit)
        response = gw.app_stub.GetLastSubmissions(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard"""
    try:
        gw = init_gateway()
        limit = request.args.get('limit', 10, type=int)
        
        grpc_request = code_executor_pb2.LeaderboardRequest(limit=limit)
        response = gw.app_stub.GetLeaderboard(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/charts/registrations', methods=['GET'])
def get_registration_chart():
    """Get registration chart data"""
    try:
        gw = init_gateway()
        days = request.args.get('days', 7, type=int)
        
        grpc_request = code_executor_pb2.ChartRequest(days=days)
        response = gw.app_stub.GetRegistrationChart(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/charts/solved-questions', methods=['GET'])
def get_solved_questions_chart():
    """Get solved questions chart data"""
    try:
        gw = init_gateway()
        days = request.args.get('days', 7, type=int)
        
        grpc_request = code_executor_pb2.ChartRequest(days=days)
        response = gw.app_stub.GetSolvedQuestionsChart(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/charts/activity', methods=['GET'])
def get_activity_stats():
    """Get activity statistics"""
    try:
        gw = init_gateway()
        days = request.args.get('days', 7, type=int)
        
        grpc_request = code_executor_pb2.ActivityStatsRequest(days=days)
        response = gw.app_stub.GetActivityStats(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/notebook/summary', methods=['POST'])
def process_notebook():
    """Process notebook summary"""
    try:
        gw = init_gateway()
        data = request.get_json()
        
        grpc_request = Parse(json.dumps(data), code_executor_pb2.NotebookSummaryRequest())
        response = gw.app_stub.ProcessNotebookSummary(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/events/trigger', methods=['POST'])
def trigger_event():
    """Trigger event"""
    try:
        gw = init_gateway()
        data = request.get_json()
        
        grpc_request = Parse(json.dumps(data), code_executor_pb2.TriggerEventRequest())
        response = gw.app_stub.TriggerEvent(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_app.route('/api/v1/instagram/posts', methods=['GET'])
def get_instagram_posts():
    """Get Instagram posts"""
    try:
        gw = init_gateway()
        username = request.args.get('username', '')
        limit = request.args.get('limit', 10, type=int)
        
        grpc_request = code_executor_pb2.InstagramPostsRequest(username=username, limit=limit)
        response = gw.app_stub.GetInstagramPosts(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Root endpoint
@gateway_app.route('/')
def index():
    """API documentation"""
    return jsonify({
        "name": "Python Playground gRPC-HTTP Gateway",
        "version": "1.0.0",
        "description": "HTTP/JSON REST API for gRPC services",
        "endpoints": {
            "executor": {
                "POST /api/v1/executor/execute": "Execute code with test cases",
                "POST /api/v1/executor/validate": "Validate code syntax",
                "POST /api/v1/executor/language-info": "Get language info"
            },
            "application": {
                "GET /api/v1/status": "Get server status",
                "GET /api/v1/health": "Health check",
                "GET /api/v1/users/recent": "Get recent users",
                "GET /api/v1/users/<username>/profile": "Get user profile",
                "GET /api/v1/questions/recent": "Get recent questions",
                "POST /api/v1/questions/generate": "Generate AI question",
                "POST /api/v1/questions/save": "Save question",
                "GET /api/v1/submissions/recent": "Get recent submissions",
                "GET /api/v1/leaderboard": "Get leaderboard",
                "GET /api/v1/charts/registrations": "Registration chart",
                "GET /api/v1/charts/solved-questions": "Solved questions chart",
                "GET /api/v1/charts/activity": "Activity statistics",
                "POST /api/v1/notebook/summary": "Process notebook",
                "POST /api/v1/events/trigger": "Trigger event",
                "GET /api/v1/instagram/posts": "Get Instagram posts"
            }
        },
        "docs": "Visit endpoints for automatic JSON response"
    })


def start_gateway(host='0.0.0.0', port=8080):
    """Start the HTTP gateway server"""
    logger.info("=" * 60)
    logger.info("🌉 Starting gRPC-HTTP Gateway")
    logger.info("=" * 60)
    logger.info(f"🌐 HTTP Server: http://{host}:{port}")
    logger.info(f"📡 gRPC Executor: {gateway.grpc_executor_host if gateway else 'localhost:50051'}")
    logger.info(f"📡 gRPC Application: {gateway.grpc_app_host if gateway else 'localhost:50060'}")
    logger.info("=" * 60)
    
    gateway_app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    init_gateway()
    start_gateway()

