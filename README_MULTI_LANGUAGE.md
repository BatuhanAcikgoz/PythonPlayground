# Multi-Language Code Execution Platform

## 🎯 Yeni Mimari Özellikleri

### ✨ Multi-Language Desteği

Proje artık sadece Python değil, **Python, R ve MATLAB** için kod değerlendirme desteği sunuyor!

### 🏗️ gRPC Tabanlı Mikro-servis Mimarisi

#### Neden gRPC?

1. **Dil Bağımsızlığı**: Her dil için ayrı izole executor servisleri
2. **Yüksek Performans**: Binary protokol ile hızlı iletişim
3. **Ölçeklenebilirlik**: Her servis bağımsız scale edilebilir
4. **Güvenlik**: Sandboxed execution environments
5. **Bakım Kolaylığı**: Her dil için ayrı container

## 📂 Yeni Yapı

```
ProgrammingPlayground/
├── protos/
│   └── code_executor.proto          # gRPC servis tanımları
├── grpc_services/
│   ├── python_executor.py           # Python kod çalıştırıcı
│   ├── r_executor.py                # R kod çalıştırıcı
│   ├── matlab_executor.py           # MATLAB/Octave çalıştırıcı
│   ├── executor_client.py           # gRPC client
│   └── server.py                    # Birleşik gRPC server
├── app/
│   ├── services/
│   │   └── code_execution_service.py # Multi-language execution service
│   └── models/
│       └── programming_question.py   # UPDATED: language field eklendi
├── Dockerfile.python-executor       # Python executor container
├── Dockerfile.r-executor            # R executor container
├── Dockerfile.matlab-executor       # MATLAB executor container
└── docker-compose.multi-language.yml # Orchestration
```

## 🚀 Kurulum ve Çalıştırma

### 1. gRPC Kod Üretimi

```bash
# Proto dosyalarından Python kodu üret
chmod +x generate_grpc.sh
./generate_grpc.sh
```

### 2. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 3. Database Migration

```bash
# Language field'ı ekle
python migrations/add_language_field.py
```

### 4. Docker ile Tüm Servisleri Başlat

```bash
# Tüm servisleri (Python, R, MATLAB executors) başlat
docker-compose -f docker-compose.multi-language.yml up --build
```

### 5. Manuel Olarak Executor Servisleri Başlatma (Development)

```bash
# Terminal 1 - Python Executor
python -m grpc_services.python_executor

# Terminal 2 - R Executor  
python -m grpc_services.r_executor

# Terminal 3 - MATLAB Executor
python -m grpc_services.matlab_executor

# VEYA hepsini birden:
python grpc_services/server.py
```

### 6. Ana Flask Uygulamasını Başlat

```bash
python app.py
```

## 🔧 Kullanım

### Yeni Soru Ekleme (Multi-Language)

```python
from app.models.programming_question import ProgrammingQuestion

# Python Sorusu
python_question = ProgrammingQuestion(
    title="Fibonacci Dizisi",
    description="Fibonacci dizisinin n. elemanını hesaplayın",
    language="python",  # NEW!
    function_name="fibonacci",
    difficulty=2,
    points=20,
    test_inputs='[[0], [1], [5], [10]]',
    solution_code='''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
)

# R Sorusu
r_question = ProgrammingQuestion(
    title="Vektör Ortalaması",
    description="Bir vektörün ortalamasını hesaplayın",
    language="r",  # NEW!
    function_name="calculate_mean",
    difficulty=1,
    points=10,
    test_inputs='[[[1,2,3,4,5]], [[10,20,30]]]',
    solution_code='''
calculate_mean <- function(vec) {
    return(mean(vec))
}
'''
)

# MATLAB Sorusu
matlab_question = ProgrammingQuestion(
    title="Matris Determinantı",
    description="Bir matrisin determinantını hesaplayın",
    language="matlab",  # NEW!
    function_name="matrix_det",
    difficulty=3,
    points=30,
    test_inputs='[[[1,2],[3,4]], [[5,6],[7,8]]]',
    solution_code='''
function result = matrix_det(matrix)
    result = det(matrix);
end
'''
)
```

### API Kullanımı

```python
from app.services.code_execution_service import get_code_execution_service

service = get_code_execution_service()

# Python kodu çalıştır
result = service.execute_solution(
    language='python',
    code='def add(a, b): return a + b',
    function_name='add',
    test_inputs='[[1, 2], [5, 3]]',
    solution_code='def add(a, b): return a + b'
)

# R kodu çalıştır
result = service.execute_solution(
    language='r',
    code='add <- function(a, b) { return(a + b) }',
    function_name='add',
    test_inputs='[[1, 2], [5, 3]]'
)

# MATLAB kodu çalıştır
result = service.execute_solution(
    language='matlab',
    code='function result = add(a, b); result = a + b; end',
    function_name='add',
    test_inputs='[[1, 2], [5, 3]]'
)
```

## 🎨 Frontend Değişiklikleri

Soru listesinde dil badge'i göstermek için:

```html
<div class="question-card">
    <span class="language-badge badge-{{ question.language }}">
        {{ question.get_language_display() }}
    </span>
    <h3>{{ question.title }}</h3>
</div>
```

## 🐳 Docker Servisleri

### Servis Portları

- **Flask App**: 5000
- **Python Executor**: 50051 (gRPC)
- **R Executor**: 50052 (gRPC)
- **MATLAB Executor**: 50053 (gRPC)
- **MySQL**: 3306
- **Redis**: 6379

### Resource Limits

Her executor servisi için:
- **CPU**: 1.0 core
- **Memory**: 512MB (Python/R), 1GB (MATLAB)
- **Timeout**: 5 saniye (default)

## 🔒 Güvenlik

1. **Sandboxed Execution**: Her kod ayrı process'te çalışır
2. **Resource Limits**: Memory ve CPU limitleri
3. **Timeout Protection**: Sonsuz döngülere karşı koruma
4. **Container Isolation**: Docker container izolasyonu

## 📊 Performans

- gRPC binary protokol ile düşük latency
- Concurrent execution desteği
- Her dil için ayrı worker pool
- Redis caching desteği (optional)

## 🧪 Test

```bash
# Unit tests
pytest tests/

# Executor servislerini test et
python -m pytest tests/test_executors.py

# Integration tests
python -m pytest tests/test_multi_language_integration.py
```

## 🔄 Migration Path

Mevcut Python sorularını güncelleme:

```python
# Tüm mevcut soruları Python olarak işaretle
from app.models.programming_question import ProgrammingQuestion

questions = ProgrammingQuestion.query.all()
for q in questions:
    if not q.language:
        q.language = 'python'
db.session.commit()
```

## 📈 Gelecek Geliştirmeler

- [ ] JavaScript/TypeScript desteği
- [ ] Java desteği
- [ ] C/C++ desteği
- [ ] Go desteği
- [ ] Real-time collaboration
- [ ] Code diff ve versioning
- [ ] Performance metrics dashboard

## 🤝 Katkıda Bulunma

Yeni dil desteği eklemek için:

1. `grpc_services/{lang}_executor.py` oluştur
2. `Dockerfile.{lang}-executor` ekle
3. `docker-compose.multi-language.yml` güncelle
4. Test case'leri ekle

## 📝 Lisans

[Mevcut lisans bilgileriniz]

---

**Not**: Bu yeni mimari geriye uyumludur. Mevcut Python soruları çalışmaya devam edecektir.
# gRPC Services Package

