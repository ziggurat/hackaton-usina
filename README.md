# Instructions to run the app locally (both front and back)
## Front end setup

1. Install node
2. Change to front-end folder
    ```bash 
    cd front-end
    ```
3. Install dependencies
    ```bash
    npm install
    ```
4. Build the site (El build generará la carpeta dist con la app, que es servida por el backend.)
    ```bash
    npm run build
    ```

## Backend setup

1. Install uv
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. Install Python
    ```bash
    uv python install 3.10
    ```

3. Setup Python virtual Environment
    ```bash
    uv venv --python 3.10
    source .venv/bin/activate
    ```

4. Install dependencies
    ```bash
    uv pip install -r requirements.txt
    ```

5. Configure the environment variables. Create a .env file with these variables:
    ```properties
    OPENAI_API_KEY = <Your OpenAI API key>
    LLM_MODEL = gpt-4o-mini

    EMBEDDINGS_MODEL="text-embedding-3-small" 
    TRAMITES_DB="./tramites/tramites_db"
    ORGANIGRAMA_DB="sqlite:///organigrama/usina.db"
    HISTORIA_DB="./historia/output/historia_db"
    ```

## Start the app
    uvicorn router.main:app --reload --log-level debug    