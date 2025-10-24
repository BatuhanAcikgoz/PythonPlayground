# gRPC to HTTP/JSON Gateway

Bu sistem, gRPC servislerinizi HTTP/JSON REST API formatında erişilebilir hale getirir.

## 🎯 Avantajlar

✅ **FastAPI'ye gerek yok** - gRPC doğrudan HTTP/JSON'a dönüştürülür
✅ **Yüksek performans** - gRPC'nin hızını korur
✅ **Kolay test** - Postman, curl veya tarayıcıdan test edebilirsiniz
✅ **JSON format** - Standart REST API gibi kullanım

## 🏗️ Mimari

```
Client (HTTP/JSON)
    ↓
HTTP Gateway (Port 8080)
    ↓
gRPC Services
    ├── Code Executor (Port 50051)
    └── Application Service (Port 50060)
```

## 📦 Kurulum

1. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

2. Proto dosyalarını derleyin:
```bash
bash generate_grpc.sh
```

## 🚀 Başlatma

### Tüm servisleri tek komutla başlatın:
```bash
python start_grpc_services.py
```

Bu komut:
- gRPC Code Executor servisini başlatır (Port 50051)
- gRPC Application servisini başlatır (Port 50060)
- HTTP/JSON Gateway'i başlatır (Port 8080)

### Ayrı ayrı başlatma (opsiyonel):

**1. gRPC Servisleri:**
```bash
python -m app.grpc_services.server
```

**2. HTTP Gateway:**
```bash
python -m app.grpc_services.grpc_http_gateway
```

## 📡 API Endpoints

### Root Endpoint
```bash
GET http://localhost:8080/
```
Tüm kullanılabilir endpoint'leri listeler.

### Code Execution Service

**Execute Code:**
```bash
POST http://localhost:8080/api/v1/executor/execute
Content-Type: application/json

{
  "language": 1,
  "code": "def add(a, b):\n    return a + b",
  "function_name": "add",
  "test_cases": [
    {
      "input_json": "{\"a\": 2, \"b\": 3}",
      "expected_output": "5",
      "timeout_ms": 1000
    }
  ]
}
```

**Validate Syntax:**
```bash
POST http://localhost:8080/api/v1/executor/validate
Content-Type: application/json

{
  "language": 1,
  "code": "def hello():\n    print('Hello')"
}
```

**Get Language Info:**
```bash
POST http://localhost:8080/api/v1/executor/language-info
Content-Type: application/json

{
  "language": 1
}
```

### Application Service

**Server Status:**
```bash
GET http://localhost:8080/api/v1/status
```

**Health Check:**
```bash
GET http://localhost:8080/api/v1/health
```

**Recent Users:**
```bash
GET http://localhost:8080/api/v1/users/recent?limit=10
```

**User Profile:**
```bash
GET http://localhost:8080/api/v1/users/{username}/profile
```

**Recent Questions:**
```bash
GET http://localhost:8080/api/v1/questions/recent?limit=10
```

**Generate Question (AI):**
```bash
POST http://localhost:8080/api/v1/questions/generate
Content-Type: application/json

{
  "topic": "list operations",
  "difficulty": "medium",
  "language": "python",
  "additional_requirements": "Should include edge cases"
}
```

**Save Question:**
```bash
POST http://localhost:8080/api/v1/questions/save
Content-Type: application/json

{
  "title": "Sum Two Numbers",
  "description": "Write a function that sums two numbers",
  "difficulty": 1,
  "points": 10,
  "function_name": "add",
  "solution_code": "def add(a, b):\n    return a + b",
  "test_inputs": "[{\"a\": 2, \"b\": 3}]",
  "example_input": "2, 3",
  "example_output": "5",
  "language": "python"
}
```

**Recent Submissions:**
```bash
GET http://localhost:8080/api/v1/submissions/recent?limit=10
```

**Leaderboard:**
```bash
GET http://localhost:8080/api/v1/leaderboard?limit=20
```

**Registration Chart:**
```bash
GET http://localhost:8080/api/v1/charts/registrations?days=7
```

**Solved Questions Chart:**
```bash
GET http://localhost:8080/api/v1/charts/solved-questions?days=30
```

**Activity Statistics:**
```bash
GET http://localhost:8080/api/v1/charts/activity?days=14
```

**Process Notebook:**
```bash
POST http://localhost:8080/api/v1/notebook/summary
Content-Type: application/json

{
  "notebook_path": "/path/to/notebook.ipynb",
  "language": "python"
}
```

**Trigger Event:**
```bash
POST http://localhost:8080/api/v1/events/trigger
Content-Type: application/json

{
  "event_type": "user_registered",
  "event_data_json": "{\"user_id\": 123}"
}
```

**Instagram Posts:**
```bash
GET http://localhost:8080/api/v1/instagram/posts?username=example&limit=12
```

## 🧪 Test Etme

### Curl ile test:
```bash
# Health check
curl http://localhost:8080/api/v1/health

# Server status
curl http://localhost:8080/api/v1/status

# Execute code
curl -X POST http://localhost:8080/api/v1/executor/execute \
  -H "Content-Type: application/json" \
  -d '{
    "language": 1,
    "code": "def multiply(a, b):\n    return a * b",
    "function_name": "multiply",
    "test_cases": [
      {
        "input_json": "{\"a\": 3, \"b\": 4}",
        "expected_output": "12",
        "timeout_ms": 1000
      }
    ]
  }'
```

### Python ile test:
```python
import requests

# Health check
response = requests.get('http://localhost:8080/api/v1/health')
print(response.json())

# Execute code
response = requests.post(
    'http://localhost:8080/api/v1/executor/execute',
    json={
        'language': 1,  # Python
        'code': 'def add(a, b):\n    return a + b',
        'function_name': 'add',
        'test_cases': [
            {
                'input_json': '{"a": 5, "b": 7}',
                'expected_output': '12',
                'timeout_ms': 1000
            }
        ]
    }
)
print(response.json())
```

## 🔧 Yapılandırma

Gateway yapılandırması için `grpc_http_gateway.py` dosyasını düzenleyin:

```python
# gRPC server adresleri
GRPC_EXECUTOR_HOST = 'localhost:50051'
GRPC_APP_HOST = 'localhost:50060'

# HTTP Gateway portu
HTTP_PORT = 8080
```

## 📊 Language Enum

Proto dosyasındaki language değerleri:
- `0` - LANGUAGE_UNSPECIFIED
- `1` - PYTHON
- `2` - R
- `3` - MATLAB

## 🐛 Hata Ayıklama

Log seviyesini değiştirmek için:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Güvenlik Notları

- Üretim ortamında CORS ayarlarını sıkılaştırın
- Rate limiting ekleyin
- Authentication/Authorization uygulayın
- HTTPS kullanın

## 📝 Ek Notlar

- Tüm response'lar JSON formatındadır
- gRPC hataları HTTP status kodlarına dönüştürülür
- Proto field isimleri snake_case olarak korunur
- Binary veriler base64 encode edilmez (bytes olarak gelir)

## 🎉 Sonuç

Artık FastAPI'ye ihtiyacınız yok! Tüm API isteklerinizi HTTP/JSON formatında yapabilirsiniz ve arka planda gRPC'nin performansından yararlanırsınız.

