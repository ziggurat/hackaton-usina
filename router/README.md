# Setup Instructions

## 1. Installing uv

- Install uv:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Load into environment:
  ```bash
  source $HOME/.local/bin/env  # (sh, bash, zsh)
  ```

## 2. Installing Python

- Install Python using uv (make sure you install a Python version NOT BIGGER THAN Python 3.10):
  ```bash
  uv python install 3.10
  ```

## 3. Virtual Environment

- Create the virtual environment for Python and activate it:
  ```bash
  uv venv --python 3.10
  source .venv/bin/activate
  ```

## 4. Dependencies

- Install dependencies:
  ```bash
  uv pip install -r requirements.txt
  ```


## 5. Configure the environment variables

- You need to create a .env file with these variables:
  
  ```properties 
  OPENAI_API_KEY =

  AWS_ACCESS_KEY_ID =
  AWS_SECRET_ACCESS_KEY =
  
  AWS_REGION=
  S3_BUCKET_NAME=
  ```

## 6. Run it (development mode)
  
  ```bash
  fastapi dev main.py
  ```
