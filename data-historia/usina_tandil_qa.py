from chromadb.utils.data_loaders import ImageLoader
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from langchain_chroma import Chroma
import chromadb
import base64
import os
import io
import traceback

from dotenv import load_dotenv

load_dotenv()


class UsinaTandilQA:
    def __init__(self):
        self.image_loader = ImageLoader()
        self.db_path = os.environ.get('OUTPUT_PATH') + os.environ.get('DB_NAME')
        self.collection_name = os.environ.get('COLLECTION_NAME')

        self.chroma_client = chromadb.PersistentClient(path=self.db_path)
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=self.collection_name,
            embedding_function=OpenCLIPEmbeddings(
                model_name="ViT-B-32", checkpoint="laion2b_s34b_b79k"
            ),
        )

        self.llm = ChatOpenAI(model='o3-mini')

        # Definir pipeline RAG
        self.chain = (
            {
                "context": self.create_text_retriever() | RunnableLambda(self.split_image_text_types),
                "question": RunnablePassthrough(),
            }
            | RunnableLambda(self.prompt_func)
            | self.llm
            | StrOutputParser()
        )

    def create_text_retriever(self):
        """Crea el recuperador de textos desde la base vectorial."""
        return self.vector_store.as_retriever()

    def is_base64(self, s):
        """Verifica si una cadena es Base64."""
        try:
            return base64.b64encode(base64.b64decode(s)) == s.encode()
        except Exception:
            return False

    def resize_base64_image(self, base64_string, size=(128, 128)):
        """Redimensiona una imagen en Base64."""
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data))
        resized_img = img.resize(size, Image.LANCZOS)

        buffered = io.BytesIO()
        resized_img.save(buffered, format=img.format)

        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def split_image_text_types(self, docs):
        """Separa imágenes (Base64) y textos de los documentos recuperados."""
        images = []
        texts = []
        for doc in docs:
            doc = doc.page_content
            if self.is_base64(doc):
                images.append(self.resize_base64_image(doc, size=(250, 250)))
            else:
                texts.append(doc)
        return {"images": images, "texts": texts}

    def prompt_func(self, data_dict):
        # Joining the context texts into a single string
        formatted_texts = "\n".join(data_dict["context"]["texts"])
        messages = []

        # Adding image(s) to the messages if present
        if data_dict["context"]["images"]:
            image_message = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{data_dict['context']['images']}"
                },
            }
            messages.append(image_message)

        print("data dict question: " + data_dict['question'])

        text_message_initial = {
            "type": "text",
            "text": (
                "Como experto en preguntas analiza si la pregunta realizada es directa o si es abierta. "
                "Una pregunta directa pide datos concretos. Una pregunta abierta requiere contexto, análisis histórico, resúmenes, comparativas.\n"
                "- Decidir si la pregunta del usuario es directa o abierta.\n"
                #"Clasifica la pregunta en una de las siguientes categorías:\n"
                #"- Pregunta directa: Pregunta que no necesita de contexto adicional para ser respondida.\n"
                #"- Pregunta abierta: Pregunta que necesita de contexto adicional para ser respondida.\n"
                "Instrucciones:\n"
                "- NO incluyas el tipo de pregunta en la respuesta."
            )
        }
        messages.append(text_message_initial)
        initial_response = [HumanMessage(content=messages)]

        #print("initial response: \n")
        #print(initial_response)
        #print("\n")

        # Adding the text message for analysis
        text_message = {
            "type": "text",
            "text": (
                "Como historiador experto y particularmente en la historia de la Usina de Tandil, tu tarea es analizar e interpretar textos e imágenes "
                "considerando su importancia histórica y cultural. Ambos se recuperarán de una vectorstore basada "
                "en las palabras clave ingresadas por el usuario. Utiliza tu amplio conocimiento y habilidades analíticas para proporcionar una "
                "respuesta analizando los chunks minuciosamente y filtrando información similar dependiendo el contexto histórico y cronológico.\n"
                #f"La pregunta del usuario es: {initial_response}\n"
                "Si la pregunta es abierta haz lo siguiente:\n"
                "- Responde la pregunta entre 300 y 1000 caracteres.\n"
                "- El contexto histórico y cultural del texto (si corresponde).\n"
                "- Conexiones entre el texto y la imagen (si la hay).\n"
                
                "Si la pregunta es concisa haz lo siguiente:\n"
                "- Responde la pregunta en no más de 300 caracteres.\n"
                "Instrucciones:\n"
                "- Evalúa la cronología de los eventos para contrastar hechos y fechas correctamente.\n"
                "- Brinda tu respuesta en español.\n"
                "- Trae una única imagen.\n"
                "- La respuesta NO debe incluir el análisis previo.\n"
                "- NO INVENTES. Limitate estrictamente al contexto proporcionada.\n"
                f"Palabras clave proporcionadas por el usuario: {data_dict['question']}\n\n"
                "Texto y/o tablas:\n"
                f"{formatted_texts}"
            ),
        }
        messages.append(text_message)
        final_response = [HumanMessage(content=messages)]

        #final_response.pop(0)
        #print("final response: \n")
        #print(final_response)
        #print("\n")

        return final_response

    def run_query(self, query):
        """Ejecuta la consulta y devuelve la respuesta."""
        if not query:
            return "No se ingresó ninguna consulta."

        docs = self.create_text_retriever().invoke(query, k=6)

        if not docs:
            return "No hay resultados para la consulta."

        print("\nDocumentos recuperados:")
        for doc in docs:
            print("\n", doc.page_content)

        response = self.chain.invoke(query)

        return f"\nRESPUESTA FINAL GENERADA:\n\n{response}"
