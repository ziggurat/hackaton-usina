from dotenv import load_dotenv

# Cargar variables de entorno
# load_dotenv()
import os
from pathlib import Path
import sys

ENV_PATH = Path('.') / 'usina.env'
result = load_dotenv(dotenv_path=ENV_PATH.resolve(), override=True)
# print("Reading OPENAI config:", ENV_PATH.resolve(), result)
os.environ["OPENAI_MODEL_NAME"] =  os.getenv('LLM_MODEL') # 'gpt-4o-mini'
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["EMBEDDINGS_MODEL"] = os.getenv("EMBEDDINGS_MODEL")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["ORGANIGRAMA_DB"] = os.getenv("ORGANIGRAMA_DB")    
print(os.environ["OPENAI_MODEL_NAME"])
# print(os.environ["EMBEDDINGS_MODEL"])
print(os.environ["ORGANIGRAMA_DB"])

from query_processor import QueryProcessor

# Ejemplo de uso
if __name__ == "__main__":
    consultor = QueryProcessor()
    
    while True:
        pregunta = input("Ingresa tu pregunta sobre personas y organigrama (o 'salir' para terminar): ")
        if pregunta.lower() == 'salir':
            break
            
        respuesta = consultor.consultar(pregunta)
        print(respuesta)