# Setup Instructions

## 1. Installing uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Installing Python

```bash
uv python install 3.10
```

## 3. Virtual Environment

```bash
uv venv --python 3.10
source .venv/bin/activate
```

## 4. Dependencies

```bash
uv pip install -r requirements.txt
```

## 5. Configure the environment variables

Create a .env file with these variables:
  
```properties
OPENAI_API_KEY =

AWS_ACCESS_KEY_ID =
AWS_SECRET_ACCESS_KEY =

AWS_REGION=
S3_BUCKET_NAME=
```

## 6. Server
  
```bash
uvicorn router.main:app --reload --log-level debug
```

## 7. Frontend

```bash
node -v   
v22.14.0
```

```bash
npm install
```

```bash
npm run build
```

El build generará la carpeta dist con la app, que es servida por el backend.
