from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import platform
import psutil
import flask
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Veritabanı bağlantısı
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

api = FastAPI(title="Python Platform API", version="1.0.0")

# CORS ekle - domain sınırlaması
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],  # Sadece Flask uygulamasının adresine izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Veritabanı oturumu dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Admin yetkilendirme (basit)
def get_current_admin():
    # Gerçek bir uygulamada JWT token vb. ile yetkilendirme yapılmalı
    return {"is_admin": True}


class ServerStatus(BaseModel):
    python_version: str
    flask_version: str
    mysql_version: str
    ram_used: float
    ram_total: float
    cpu_usage: float
    process_ram_used: float
    process_ram_allocated: float


@api.get("/api/server-status", response_model=ServerStatus)
def server_status(admin: dict = Depends(get_current_admin), db=Depends(get_db)):
    # Python sürümü
    python_version = platform.python_version()

    # Flask sürümü
    flask_version = flask.__version__

    # MySQL sürümü
    mysql_result = db.execute(text("SELECT VERSION() as version")).first()
    mysql_version = mysql_result.version if mysql_result else "Unknown"

    # Sistem RAM kullanımı
    mem = psutil.virtual_memory()
    ram_used = round(mem.used / (1024 * 1024 * 1024), 2)  # GB
    ram_total = round(mem.total / (1024 * 1024 * 1024), 2)  # GB

    # Süreç RAM kullanımı
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    process_ram_used = round(process_memory.rss / (1024 * 1024 * 1024), 2)
    process_ram_allocated = round(process_memory.vms / (1024 * 1024 * 1024), 2)

    # CPU kullanımı
    cpu_usage = psutil.cpu_percent(interval=1)

    return {
        'python_version': python_version,
        'flask_version': flask_version,
        'mysql_version': mysql_version,
        'ram_used': ram_used,
        'ram_total': ram_total,
        'cpu_usage': cpu_usage,
        'process_ram_used': process_ram_used,
        'process_ram_allocated': process_ram_allocated
    }


# User model - sadece API amaçlı
class UserRole(BaseModel):
    id: int
    name: str


class UserData(BaseModel):
    id: int
    username: str
    email: str
    registered: str
    roles: List[str]


@api.get("/api/recent-users", response_model=List[UserData])
def recent_users(admin: dict = Depends(get_current_admin), db=Depends(get_db)):
    # Doğru import edilmiş text() kullanımı
    sql_query = text("""
        SELECT u.id, u.username, u.email, u.created_at
        FROM user u
        ORDER BY u.id DESC
        LIMIT 5
    """)

    result = db.execute(sql_query)

    users = []
    for row in result:
        # Kullanıcı rollerini al
        roles_query = text("""
            SELECT r.id, r.name
            FROM role r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = :user_id
        """)

        roles_result = db.execute(roles_query, {"user_id": row.id})

        roles = [role.name for role in roles_result]

        users.append({
            "id": row.id,
            "username": row.username,
            "email": row.email,
            "registered": row.created_at.strftime('%Y-%m-%d'),
            "roles": roles
        })

    return users


class Question(BaseModel):
    id: int
    title: str
    user: str
    date: str
    status: str


@api.get("/api/recent-questions", response_model=List[Question])
def recent_questions(admin: dict = Depends(get_current_admin)):
    # Örnek veri
    sample_questions = [
        {
            "id": 1,
            "title": "Python döngüleri nasıl kullanılır?",
            "user": "student1",
            "date": "02.04.2025",
            "status": "answered"
        },
        {
            "id": 2,
            "title": "Flask Blueprint nedir?",
            "user": "student3",
            "date": "01.04.2025",
            "status": "pending"
        },
        {
            "id": 3,
            "title": "React ile Flask nasıl entegre edilir?",
            "user": "student2",
            "date": "31.03.2025",
            "status": "answered"
        },
        {
            "id": 4,
            "title": "SQLAlchemy ilişkiler nasıl kurulur?",
            "user": "student4",
            "date": "30.03.2025",
            "status": "pending"
        }
    ]

    return sample_questions