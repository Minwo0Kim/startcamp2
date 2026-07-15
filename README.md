# LocalHub Backend

FastAPI 기반 백엔드입니다.

## 개발 환경 설정

이 프로젝트는 `venv` 이름의 가상환경을 사용합니다. 팀원도 같은 방식으로 설정하려면 아래 순서대로 실행하면 됩니다.

### 1. 가상환경 생성

```bash
python -m venv venv
```

### 2. 가상환경 활성화

Windows CMD 또는 Git Bash:

```bash
venv\Scripts\activate
```

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. DB 초기화 및 데이터 적재

```bash
python init_db.py
```

### 5. 서버 실행

```bash
uvicorn app.main:app --reload
```

### 6. 가상환경 종료

```bash
deactivate
```

## 확인용 엔드포인트

브라우저에서 아래 주소를 열면 정상 동작 여부를 확인할 수 있습니다.

```text
http://127.0.0.1:8000/
```