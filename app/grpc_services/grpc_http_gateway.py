"""
gRPC-HTTP Gateway - JSON REST API Bridge for gRPC Services
Converts HTTP/JSON requests to gRPC calls and vice versa
"""

import grpc
import json
import logging
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import sys
import os

# Add generated proto files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

import code_executor_pb2
import code_executor_pb2_grpc

from google.protobuf.json_format import MessageToDict, Parse, ParseError

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
        
        logger.info(f"✅ gRPC Gateway bağlandı - Executor: {grpc_executor_host}, App: {grpc_app_host}")

    def __del__(self):
        """Close channels on cleanup"""
        try:
            self.executor_channel.close()
            self.app_channel.close()
        except:
            pass


# Create Blueprint instead of Flask app
api_gateway_bp = Blueprint('api_gateway', __name__)

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

@api_gateway_bp.route('/api/v1/executor/execute', methods=['POST'])
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


@api_gateway_bp.route('/api/v1/executor/validate', methods=['POST'])
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


@api_gateway_bp.route('/api/v1/executor/language-info', methods=['POST'])
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

@api_gateway_bp.route('/api/v1/status', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/health', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/users/recent', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/users/<username>/profile', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/questions/recent', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/questions/generate', methods=['POST'])
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


@api_gateway_bp.route('/api/v1/questions/save', methods=['POST'])
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


@api_gateway_bp.route('/api/v1/submissions/recent', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/leaderboard', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/charts/registrations', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/charts/solved-questions', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/charts/activity', methods=['GET'])
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


@api_gateway_bp.route('/api/v1/notebook/summary', methods=['POST'])
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


@api_gateway_bp.route('/api/v1/events/trigger', methods=['POST'])
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


@api_gateway_bp.route('/api/instagram-posts', methods=['GET'])
@api_gateway_bp.route('/api/v1/instagram-posts', methods=['GET'])
def get_instagram_posts():
    """Get Instagram posts - backward compatible endpoint"""
    try:
        gw = init_gateway()
        username = request.args.get('instagram_username', '')
        limit = request.args.get('limit', 10, type=int)
        
        grpc_request = code_executor_pb2.InstagramPostsRequest(
            username=username,
            limit=limit
        )
        response = gw.app_stub.GetInstagramPosts(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)
        
        return jsonify(result), 200
        
    except grpc.RpcError as e:
        logger.error(f"gRPC error in Instagram posts: {e.code()} - {e.details()}")
        return jsonify({"error": e.details(), "code": e.code().name, "success": False}), 500
    except Exception as e:
        logger.error(f"Error in Instagram posts: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500


@api_gateway_bp.route('/api/last-questions-detail', methods=['GET'])
@api_gateway_bp.route('/api/v1/last-questions-detail', methods=['GET'])
def get_last_questions_detail():
    """Get last questions detail - backward compatible endpoint"""
    try:
        gw = init_gateway()
        limit = request.args.get('limit', 10, type=int)

        grpc_request = code_executor_pb2.LastQuestionsRequest(limit=limit)
        response = gw.app_stub.GetLastQuestionsDetail(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)

        return jsonify(result), 200

    except grpc.RpcError as e:
        logger.error(f"gRPC error in last questions: {e.code()} - {e.details()}")
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        logger.error(f"Error in last questions: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_gateway_bp.route('/api/v1/instagram/refresh', methods=['POST'])
def refresh_instagram_cache():
    """Refresh Instagram cache"""
    try:
        gw = init_gateway()
        data = request.get_json() or {}
        username = data.get('username', '')

        grpc_request = code_executor_pb2.RefreshCacheRequest(username=username)
        response = gw.app_stub.RefreshInstagramCache(grpc_request)
        result = MessageToDict(response, preserving_proto_field_name=True)

        return jsonify(result), 200

    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_gateway_bp.route('/api/proxy-image', methods=['GET'])
@api_gateway_bp.route('/api/v1/proxy-image', methods=['GET'])
def proxy_image():
    """Proxy image - backward compatible endpoint"""
    try:
        from flask import Response
        gw = init_gateway()
        url = request.args.get('url', '')

        grpc_request = code_executor_pb2.ProxyImageRequest(url=url)
        response = gw.app_stub.ProxyImage(grpc_request)

        if response.success:
            return Response(
                response.image_data,
                mimetype=response.content_type or 'image/jpeg',
                headers={'Cache-Control': 'public, max-age=3600'}
            )
        else:
            return jsonify({"error": response.error}), 500

    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "code": e.code().name}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API DOCUMENTATION ENDPOINTS
# =============================================================================

@api_gateway_bp.route('/api/v1/docs', methods=['GET'])
@api_gateway_bp.route('/api/docs', methods=['GET'])
def api_docs():
    """Get API documentation in OpenAPI format"""
    from app.grpc_services.api_documentation import APIDocumentationGenerator

    doc_gen = APIDocumentationGenerator()
    return jsonify(doc_gen.get_openapi_spec()), 200


@api_gateway_bp.route('/api/v1/docs/endpoints', methods=['GET'])
@api_gateway_bp.route('/api/docs/endpoints', methods=['GET'])
def api_endpoints_list():
    """Get simplified list of all endpoints"""
    from app.grpc_services.api_documentation import APIDocumentationGenerator

    doc_gen = APIDocumentationGenerator()
    return jsonify({
        "endpoints": doc_gen.get_endpoints_list(),
        "total": len(doc_gen.endpoints)
    }), 200


@api_gateway_bp.route('/api/v1/docs/ui', methods=['GET'])
@api_gateway_bp.route('/api/docs/ui', methods=['GET'])
def api_docs_ui():
    """Swagger UI for API documentation"""
    from flask import render_template_string

    swagger_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Python Playground API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.0/swagger-ui.min.css">
        <style>
            body { margin: 0; padding: 0; }
            .topbar { display: none; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.0/swagger-ui-bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.0/swagger-ui-standalone-preset.min.js"></script>
        <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: "/api/v1/docs",
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    deepLinking: true,
                    showExtensions: true,
                    showCommonExtensions: true
                });
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(swagger_html)


# =============================================================================
# GATEWAY SERVER
# =============================================================================

def start_gateway(host='0.0.0.0', port=8080):
    """Start the HTTP/JSON Gateway server"""
    logger.info("=" * 70)
    logger.info("🌉 gRPC-HTTP Gateway Server Starting")
    logger.info("=" * 70)
    logger.info(f"📡 HTTP Server: http://{host}:{port}")
    logger.info(f"📚 API Docs: http://{host}:{port}/api/docs/ui")
    logger.info(f"📋 OpenAPI Spec: http://{host}:{port}/api/v1/docs")
    logger.info(f"📍 Endpoints List: http://{host}:{port}/api/docs/endpoints")
    logger.info("=" * 70)

    # Initialize gateway on startup
    init_gateway()

    from flask import Flask
    app = Flask(__name__)
    CORS(app)

    # Register the blueprint
    app.register_blueprint(api_gateway_bp)

    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    start_gateway()
