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
    
    def query_validation(self, query):
        if not query:
            return "No se ingresó ninguna consulta."
        
        messages = []
        
        text_validator = {
            "type": "text",
            "text": (
                "Role:\n"
                "Query validator\n\n"
                "Skills:\n"
                "As an expert in validation of queries or questions, you will analyze the content of the query and then clasify it \n"
                "as true or false (boolean value) regarding if matches certain specific considerations to be pointed out at the instructions\n"
                
                "Instructions:\n"
                "- Determine whether the user's question is related to the history of the Usina of Tandil, or not.\n"
                "- RESPOND only true or false regarding the validation value, NOTHING MORE"

                f"The keywords provided by the user: \n\n {query}\n\n"
            )
        }
        messages.append(text_validator)
        
        response = self.llm.invoke([HumanMessage(content=messages)])

        print(f"Query Validation Response: {response.content}")
        # verifica si la respuesta es 'true' o 'false' y devuelve booleano
        validation_result = response.content.strip().lower() == "true"
        print(f"Query Validation Result: {validation_result}")
        
        return validation_result
        


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

        #print("\n")
        #print("data dict question: " + data_dict['question'])

        text_message_initial = {
            "type": "text",
            "text": (
                "Role:\n"
                "Question Analyst\n\n"
                "Skills:\n"
                "As an expert in questions, analyze whether the given question is concise or open-ended. "
                "A concise question asks for specific data, while an open-ended question requires context, historical analysis, summaries, or comparisons.\n"
                
                "Instructions:\n"
                "- Determine whether the user's question is concise or open-ended.\n"
                "- DO NOT include the type of question in the final response."
            )
        }
        messages.append(text_message_initial)

        # Adding the text message for analysis
        text_message = {
            "type": "text",
            "text": (
                "Role:\n"
                "Historian\n\n"
                "Skills:\n"
                "As a historian specializing in the history of the Usina de Tandil, your task is to analyze and interpret texts and images "
                "while considering their historical and cultural significance. Both will be retrieved from a vector database based on "
                "ethe keywords entered by the user. Use your analytical skills to provide a "
                "response by thoroughly examining the chunks and filtering similar information depending on the historical and chronological context.\n"
                
                "Instructions regarding the QUESTION TYPE:\n"

                "If the question is open-ended, follow these steps:\n"
                "- Respond with an answer between 300 and 1000 characters.\n"
                "- Provide the historical and cultural context of the text (if applicable).\n"
                "- Identify connections between the text and the image (if any).\n"
                
                "If the question is concise, follow these steps:\n"
                "- Respond in no more than 300 characters.\n"

                 "Instructions NOT regarding the QUESTION TYPE:\n"
                "- Evaluate the chronology of events to correctly contrast facts and dates.\n"
                "- Provide the response in the same language that the question was asked.\n"
                "- If an image is relevant, retrieve only one.\n"
                #"- La respuesta NO debe incluir el análisis previo.\n"
                "- Do not repeat information if the content is redundant in the fragments.\n"
                "- Strictly adhere to the provided context, DO NOT INVENT.\n"

                f"The keywords provided by the user: \n\n {data_dict['question']}\n\n"
                "Text and/or tables:\n"
                f"{formatted_texts}"
            ),
        }
        messages.append(text_message)
        #for mess in messages:
        #   print("\n")
        #   print(mess)

        final_response = [HumanMessage(content=messages)]

        return final_response

    def run_query(self, query):
        """Ejecuta la consulta y devuelve la respuesta."""
    
        if not self.query_validation(query):
            return "El agente no podrá procesar este tipo de consulta."

        docs = self.create_text_retriever().invoke(query, k=6)
        if not docs:
            return "No hay resultados para la consulta."

        print("\nDocumentos recuperados:")
        for doc in docs:
            print("\n", doc.page_content)

        response = self.chain.invoke(query)

        return f"\nRESPUESTA FINAL GENERADA:\n\n{response}"
        
