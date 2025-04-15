# Organigrama

Aquí encontraran una base de datos sqlite pre-cargada con la información 
disponible sobre donde encontrar a cada persona dentro de la empresa.

La intención es utilizar esta base de datos para construir el caso text-to-sql
utilizando un LLM.

## Instalación

```bash
uv install
source .venv/bin/activate
```

Crear un `.env` en la raiz con el siguiente contenido:

```bash
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=<your-langsmith-api-key>
OPENAI_API_KEY=<your-openai-api-key>
```

## Uso

```bash
uv run query.py
```
