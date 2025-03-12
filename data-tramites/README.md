## Base de datos con información de los tramites

Setup the environment:

```bash
uv install
```

Extract the information from the pdf and store it into the db:

```bash
uv run create.py
```

Query the db from the terminal for testing:

```bash
uv run query.py
```
