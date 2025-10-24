"""
Application Service Implementation - gRPC
Replaces FastAPI endpoints with gRPC services
"""

import sys
import os
import json
import platform
import psutil
import flask
import grpc
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add generated proto files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

import code_executor_pb2
import code_executor_pb2_grpc

from config import Config
from app.models.user import User, Role
from app.models.programming_question import ProgrammingQuestion
from app.models.submission import Submission
from app.models.badges import Badges
from app.models.user_badges import UserBadges
from app.events import event_manager
from app.events.event_definitions import EventType


# Database setup
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ApplicationServiceImplementation(code_executor_pb2_grpc.ApplicationServiceServicer):
    """Implementation of ApplicationService gRPC"""

    def __init__(self):
        self.engine = engine

    def get_db(self):
        """Get database session"""
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()

    def GetServerStatus(self, request, context):
        """Get server status information"""
        try:
            # Get Python version
            python_version = platform.python_version()

            # Get Flask version
            flask_version = flask.__version__

            # Get MySQL version
            db = self.get_db()
            result = db.execute(text("SELECT VERSION()")).fetchone()
            mysql_version = result[0] if result else "Unknown"

            # Get system stats
            ram = psutil.virtual_memory()
            ram_used = ram.used / (1024**3)  # GB
            ram_total = ram.total / (1024**3)  # GB
            cpu_usage = psutil.cpu_percent(interval=1)

            # Process stats
            process = psutil.Process()
            process_ram_info = process.memory_info()
            process_ram_used = process_ram_info.rss / (1024**3)  # GB
            process_ram_allocated = process_ram_info.vms / (1024**3)  # GB

            return code_executor_pb2.ServerStatusResponse(
                python_version=python_version,
                flask_version=flask_version,
                mysql_version=mysql_version,
                ram_used=ram_used,
                ram_total=ram_total,
                cpu_usage=cpu_usage,
                process_ram_used=process_ram_used,
                process_ram_allocated=process_ram_allocated
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting server status: {str(e)}")
            return code_executor_pb2.ServerStatusResponse()

    def HealthCheck(self, request, context):
        """Health check endpoint"""
        return code_executor_pb2.HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat()
        )

    def GetRecentUsers(self, request, context):
        """Get recent users"""
        try:
            db = self.get_db()
            limit = request.limit if request.limit > 0 else 10

            users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()

            user_list = []
            for user in users:
                roles = [code_executor_pb2.UserRole(id=role.id, name=role.name) for role in user.roles]
                user_list.append(code_executor_pb2.UserData(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    created_at=user.created_at.isoformat() if user.created_at else '',
                    roles=roles
                ))

            return code_executor_pb2.RecentUsersResponse(users=user_list)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting recent users: {str(e)}")
            return code_executor_pb2.RecentUsersResponse()

    def GetUserProfile(self, request, context):
        """Get user profile"""
        try:
            db = self.get_db()
            user = db.query(User).filter(User.username == request.username).first()

            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return code_executor_pb2.UserProfileResponse()

            # Get user statistics
            total_submissions = db.query(Submission).filter(Submission.user_id == user.id).count()
            correct_submissions = db.query(Submission).filter(
                Submission.user_id == user.id,
                Submission.is_correct == True
            ).count()

            # Get roles
            roles = [code_executor_pb2.UserRole(id=role.id, name=role.name) for role in user.roles]

            # Get badges
            user_badges = db.query(UserBadges).filter(UserBadges.user_id == user.id).all()
            badges = []
            for ub in user_badges:
                badge = db.query(Badges).filter(Badges.id == ub.badge_id).first()
                if badge:
                    badges.append(code_executor_pb2.BadgeData(
                        id=badge.id,
                        name=badge.name,
                        description=badge.description or '',
                        icon=badge.icon or '',
                        color=badge.color or '',
                        earned_at=ub.earned_at.isoformat() if ub.earned_at else ''
                    ))

            # Get recent submissions
            recent_subs = db.query(Submission).filter(
                Submission.user_id == user.id
            ).order_by(Submission.created_at.desc()).limit(10).all()

            submissions = []
            for sub in recent_subs:
                question = db.query(ProgrammingQuestion).filter(
                    ProgrammingQuestion.id == sub.question_id
                ).first()
                submissions.append(code_executor_pb2.SubmissionData(
                    id=sub.id,
                    question_id=sub.question_id,
                    question_title=question.title if question else 'Unknown',
                    is_correct=sub.is_correct or False,
                    created_at=sub.created_at.isoformat() if sub.created_at else '',
                    execution_time=sub.execution_time or 0.0
                ))

            return code_executor_pb2.UserProfileResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at.isoformat() if user.created_at else '',
                total_submissions=total_submissions,
                correct_submissions=correct_submissions,
                total_points=user.total_points or 0,
                roles=roles,
                badges=badges,
                recent_submissions=submissions
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting user profile: {str(e)}")
            return code_executor_pb2.UserProfileResponse()

    def GetLastQuestionsDetail(self, request, context):
        """Get last questions with details"""
        try:
            db = self.get_db()
            limit = request.limit if request.limit > 0 else 10

            questions = db.query(ProgrammingQuestion).order_by(
                ProgrammingQuestion.created_at.desc()
            ).limit(limit).all()

            question_list = []
            for q in questions:
                # Calculate stats
                total_subs = db.query(Submission).filter(Submission.question_id == q.id).count()
                correct_subs = db.query(Submission).filter(
                    Submission.question_id == q.id,
                    Submission.is_correct == True
                ).count()
                success_rate = int((correct_subs / total_subs * 100)) if total_subs > 0 else 0

                question_list.append(code_executor_pb2.DetailedQuestion(
                    id=q.id,
                    title=q.title,
                    description=q.description,
                    difficulty=q.difficulty,
                    points=q.points,
                    created_at=q.created_at.isoformat() if q.created_at else '',
                    submission_count=total_subs,
                    success_rate=success_rate,
                    language=q.language or 'python'
                ))

            return code_executor_pb2.LastQuestionsResponse(questions=question_list)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting questions: {str(e)}")
            return code_executor_pb2.LastQuestionsResponse()

    def GetLastSubmissions(self, request, context):
        """Get last submissions"""
        try:
            db = self.get_db()
            limit = request.limit if request.limit > 0 else 10

            submissions = db.query(Submission).order_by(
                Submission.created_at.desc()
            ).limit(limit).all()

            submission_list = []
            for sub in submissions:
                user = db.query(User).filter(User.id == sub.user_id).first()
                question = db.query(ProgrammingQuestion).filter(
                    ProgrammingQuestion.id == sub.question_id
                ).first()

                submission_list.append(code_executor_pb2.SubmissionDetail(
                    id=sub.id,
                    user_id=sub.user_id,
                    username=user.username if user else 'Unknown',
                    question_id=sub.question_id,
                    question_title=question.title if question else 'Unknown',
                    is_correct=sub.is_correct or False,
                    created_at=sub.created_at.isoformat() if sub.created_at else '',
                    execution_time=sub.execution_time or 0.0,
                    language=sub.language or 'python'
                ))

            return code_executor_pb2.LastSubmissionsResponse(submissions=submission_list)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting submissions: {str(e)}")
            return code_executor_pb2.LastSubmissionsResponse()

    def GetLeaderboard(self, request, context):
        """Get leaderboard"""
        try:
            db = self.get_db()
            limit = request.limit if request.limit > 0 else 10

            # Query for leaderboard
            query = text("""
                SELECT 
                    u.id,
                    u.username,
                    u.total_points,
                    COUNT(DISTINCT CASE WHEN s.is_correct = TRUE THEN s.question_id END) as solved,
                    COUNT(s.id) as total_subs,
                    CASE 
                        WHEN COUNT(s.id) > 0 
                        THEN (COUNT(CASE WHEN s.is_correct = TRUE THEN 1 END) * 100.0 / COUNT(s.id))
                        ELSE 0 
                    END as success_rate
                FROM users u
                LEFT JOIN submissions s ON u.id = s.user_id
                GROUP BY u.id, u.username, u.total_points
                ORDER BY u.total_points DESC, solved DESC
                LIMIT :limit
            """)

            results = db.execute(query, {'limit': limit}).fetchall()

            entries = []
            for idx, row in enumerate(results, 1):
                entries.append(code_executor_pb2.LeaderboardEntry(
                    rank=idx,
                    user_id=row[0],
                    username=row[1],
                    total_points=row[2] or 0,
                    solved_questions=row[3] or 0,
                    total_submissions=row[4] or 0,
                    success_rate=float(row[5]) if row[5] else 0.0
                ))

            return code_executor_pb2.LeaderboardResponse(entries=entries)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting leaderboard: {str(e)}")
            return code_executor_pb2.LeaderboardResponse()

    def GetRegistrationChart(self, request, context):
        """Get registration chart data"""
        try:
            db = self.get_db()
            days = request.days if request.days > 0 else 7

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Query registrations by day
            query = text("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM users
                WHERE created_at >= :start_date AND created_at <= :end_date
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)

            results = db.execute(query, {
                'start_date': start_date,
                'end_date': end_date
            }).fetchall()

            labels = []
            data = []
            for row in results:
                labels.append(row[0].strftime('%Y-%m-%d'))
                data.append(row[1])

            return code_executor_pb2.ChartResponse(
                labels=labels,
                data=data
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting registration chart: {str(e)}")
            return code_executor_pb2.ChartResponse()

    def GetSolvedQuestionsChart(self, request, context):
        """Get solved questions chart data"""
        try:
            db = self.get_db()
            days = request.days if request.days > 0 else 7

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Query solved questions by day
            query = text("""
                SELECT 
                    DATE(s.created_at) as date,
                    COUNT(DISTINCT s.question_id) as count
                FROM submissions s
                WHERE s.is_correct = TRUE
                    AND s.created_at >= :start_date 
                    AND s.created_at <= :end_date
                GROUP BY DATE(s.created_at)
                ORDER BY DATE(s.created_at)
            """)

            results = db.execute(query, {
                'start_date': start_date,
                'end_date': end_date
            }).fetchall()

            labels = []
            data = []
            for row in results:
                labels.append(row[0].strftime('%Y-%m-%d'))
                data.append(row[1])

            return code_executor_pb2.ChartResponse(
                labels=labels,
                data=data
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting solved questions chart: {str(e)}")
            return code_executor_pb2.ChartResponse()

    def GetActivityStats(self, request, context):
        """Get activity statistics"""
        try:
            db = self.get_db()
            days = request.days if request.days > 0 else 7

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Query activity stats by day
            query = text("""
                SELECT 
                    DATE(s.created_at) as date,
                    COUNT(*) as total_submissions,
                    COUNT(CASE WHEN s.is_correct = TRUE THEN 1 END) as successful_submissions,
                    COUNT(DISTINCT s.user_id) as unique_users
                FROM submissions s
                WHERE s.created_at >= :start_date AND s.created_at <= :end_date
                GROUP BY DATE(s.created_at)
                ORDER BY DATE(s.created_at)
            """)

            results = db.execute(query, {
                'start_date': start_date,
                'end_date': end_date
            }).fetchall()

            dates = []
            submissions = []
            successful_submissions = []
            unique_users = []

            for row in results:
                dates.append(row[0].strftime('%Y-%m-%d'))
                submissions.append(row[1])
                successful_submissions.append(row[2])
                unique_users.append(row[3])

            return code_executor_pb2.ActivityStatsResponse(
                dates=dates,
                submissions=submissions,
                successful_submissions=successful_submissions,
                unique_users=unique_users
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting activity stats: {str(e)}")
            return code_executor_pb2.ActivityStatsResponse()

    def ProcessNotebookSummary(self, request, context):
        """Process notebook and generate summary"""
        try:
            import nbformat
            from pathlib import Path

            # Read notebook file
            notebook_path = Path(request.notebook_path)
            if not notebook_path.exists():
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Notebook file not found: {request.notebook_path}")
                return code_executor_pb2.NotebookSummaryResponse(
                    success=False,
                    errors=["Notebook file not found"]
                )

            # Parse notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)

            # Extract cells
            code_cells = []
            markdown_cells = []

            for cell in notebook.cells:
                if cell.cell_type == 'code':
                    code_cells.append(cell.source)
                elif cell.cell_type == 'markdown':
                    markdown_cells.append(cell.source)

            # Generate summary
            summary = f"Notebook: {notebook_path.name}\n"
            summary += f"Total cells: {len(notebook.cells)}\n"
            summary += f"Code cells: {len(code_cells)}\n"
            summary += f"Markdown cells: {len(markdown_cells)}\n"

            return code_executor_pb2.NotebookSummaryResponse(
                success=True,
                summary=summary,
                code_cells=code_cells,
                markdown_cells=markdown_cells,
                total_cells=len(notebook.cells),
                errors=[]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error processing notebook: {str(e)}")
            return code_executor_pb2.NotebookSummaryResponse(
                success=False,
                errors=[str(e)]
            )

    def GenerateQuestion(self, request, context):
        """Generate question using AI"""
        try:
            from app.services.ai_service import generate_programming_question

            # Generate question using AI service
            result = generate_programming_question(
                topic=request.topic,
                difficulty=request.difficulty,
                language=request.language,
                additional_requirements=request.additional_requirements
            )

            if result.get('success'):
                return code_executor_pb2.GenerateQuestionResponse(
                    success=True,
                    title=result.get('title', ''),
                    description=result.get('description', ''),
                    function_name=result.get('function_name', ''),
                    solution_code=result.get('solution_code', ''),
                    test_inputs=result.get('test_inputs', ''),
                    example_input=result.get('example_input', ''),
                    example_output=result.get('example_output', ''),
                    errors=[]
                )
            else:
                return code_executor_pb2.GenerateQuestionResponse(
                    success=False,
                    errors=result.get('errors', ['Unknown error'])
                )
        except ImportError:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("AI service not available")
            return code_executor_pb2.GenerateQuestionResponse(
                success=False,
                errors=["AI service not available"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error generating question: {str(e)}")
            return code_executor_pb2.GenerateQuestionResponse(
                success=False,
                errors=[str(e)]
            )

    def SaveQuestion(self, request, context):
        """Save a programming question"""
        try:
            db = self.get_db()

            # Create new question
            question = ProgrammingQuestion(
                title=request.title,
                description=request.description,
                difficulty=request.difficulty,
                points=request.points,
                function_name=request.function_name,
                solution_code=request.solution_code,
                test_inputs=request.test_inputs,
                example_input=request.example_input,
                example_output=request.example_output,
                language=request.language or 'python'
            )

            db.add(question)
            db.commit()
            db.refresh(question)

            return code_executor_pb2.SaveQuestionResponse(
                success=True,
                question_id=question.id,
                message="Question saved successfully"
            )
        except Exception as e:
            db.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error saving question: {str(e)}")
            return code_executor_pb2.SaveQuestionResponse(
                success=False,
                question_id=0,
                message=f"Error: {str(e)}"
            )

    def TriggerEvent(self, request, context):
        """Trigger an event"""
        try:
            event_data = json.loads(request.event_data_json) if request.event_data_json else {}

            # Trigger event through event manager
            event_manager.trigger(request.event_type, event_data)

            return code_executor_pb2.TriggerEventResponse(
                success=True,
                message=f"Event {request.event_type} triggered successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error triggering event: {str(e)}")
            return code_executor_pb2.TriggerEventResponse(
                success=False,
                message=str(e)
            )

    def GetInstagramPosts(self, request, context):
        """Get Instagram posts"""
        try:
            from app.services.instagram_service import get_instagram_posts

            posts_data = get_instagram_posts(
                username=request.username,
                limit=request.limit or 12
            )

            if not posts_data.get('success'):
                return code_executor_pb2.InstagramPostsResponse(
                    posts=[],
                    success=False,
                    error=posts_data.get('error', 'Unknown error')
                )

            proto_posts = []
            for post in posts_data.get('posts', []):
                proto_posts.append(
                    code_executor_pb2.InstagramPost(
                        id=post.get('id', ''),
                        shortcode=post.get('shortcode', ''),
                        caption=post.get('caption', ''),
                        thumbnail_url=post.get('thumbnail_url', ''),
                        display_url=post.get('display_url', ''),
                        likes=post.get('likes', 0),
                        comments=post.get('comments', 0),
                        timestamp=post.get('timestamp', ''),
                        is_video=post.get('is_video', False)
                    )
                )

            return code_executor_pb2.InstagramPostsResponse(
                posts=proto_posts,
                success=True,
                error=''
            )
        except ImportError:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("Instagram service not available")
            return code_executor_pb2.InstagramPostsResponse(
                posts=[],
                success=False,
                error="Instagram service not available"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting Instagram posts: {str(e)}")
            return code_executor_pb2.InstagramPostsResponse(
                posts=[],
                success=False,
                error=str(e)
            )

    def RefreshInstagramCache(self, request, context):
        """Refresh Instagram cache"""
        try:
            from app.services.instagram_service import refresh_instagram_cache

            result = refresh_instagram_cache(request.username)

            return code_executor_pb2.RefreshCacheResponse(
                success=result.get('success', False),
                message=result.get('message', ''),
                posts_count=result.get('posts_count', 0)
            )
        except ImportError:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("Instagram service not available")
            return code_executor_pb2.RefreshCacheResponse(
                success=False,
                message="Instagram service not available",
                posts_count=0
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error refreshing cache: {str(e)}")
            return code_executor_pb2.RefreshCacheResponse(
                success=False,
                message=str(e),
                posts_count=0
            )

    def ProxyImage(self, request, context):
        """Proxy image request"""
        try:
            import requests

            response = requests.get(request.url, timeout=10)

            if response.status_code == 200:
                return code_executor_pb2.ProxyImageResponse(
                    image_data=response.content,
                    content_type=response.headers.get('Content-Type', 'image/jpeg'),
                    success=True,
                    error=''
                )
            else:
                return code_executor_pb2.ProxyImageResponse(
                    image_data=b'',
                    content_type='',
                    success=False,
                    error=f"HTTP {response.status_code}"
                )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error proxying image: {str(e)}")
            return code_executor_pb2.ProxyImageResponse(
                image_data=b'',
                content_type='',
                success=False,
                error=str(e)
            )
