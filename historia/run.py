import sys

import chromadb

from dotenv import load_dotenv

# load_dotenv()
import os
from pathlib import Path


ENV_PATH = Path('.') / 'usina.env'
result = load_dotenv(dotenv_path=ENV_PATH.resolve(), override=True)
# print("Reading OPENAI config:", ENV_PATH.resolve(), result)
os.environ["OPENAI_MODEL_NAME"] =  os.getenv('LLM_MODEL') # 'gpt-4o-mini'
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["EMBEDDINGS_MODEL"] = os.getenv("EMBEDDINGS_MODEL")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HISTORIA_DB"] = os.getenv("HISTORIA_DB")
print(os.environ["OPENAI_MODEL_NAME"])
# print(os.environ["EMBEDDINGS_MODEL"]
print(os.environ["HISTORIA_DB"])

from usina_tandil_qa import UsinaTandilQA

def main():
    client = chromadb.PersistentClient(path="./data-historia/output/historia_db")  # or HttpClient()
    collections = client.list_collections()
    print(collections)

    # query = input("Preguntá algo acerca de la historia de la Usina:")
    # qa_system = UsinaTandilQA()
    # response = qa_system.run_query(query)
    # print(response)

# Ejemplo de uso
if __name__ == "__main__":
    # main()
    consultor = UsinaTandilQA()
    
    while True:
        pregunta = input("Ingresa tu pregunta sobre historia (o 'salir' para terminar): ")
        if pregunta.lower() == 'salir':
            break
            
        respuesta = consultor.consultar(pregunta)
        print(respuesta)
