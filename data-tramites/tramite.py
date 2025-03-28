import chromadb
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv

load_dotenv()

class ConsultorTramites:
    def __init__(self, db_path="./tramites_db", collection_name="tramites", 
                 model_name="gpt-4o", embed_model="sentence-transformers/all-MiniLM-L6-v2",
                 top_k=3):
        """
        Inicializa el consultor de trámites
        
        Args:
            db_path (str): Ruta a la base de datos de ChromaDB
            collection_name (str): Nombre de la colección en ChromaDB
            model_name (str): Modelo de OpenAI a utilizar
            embed_model (str): Modelo de embeddings a utilizar
            top_k (int): Número de documentos a recuperar
        """
        # Configuración
        self.db_path = db_path
        self.collection_name = collection_name
        self.model_name = model_name
        self.embed_model = embed_model
        self.top_k = top_k
        
        # Inicialización del sistema RAG
        self._setup_rag_chain()
        
    def _setup_rag_chain(self):
        """
        Configura la cadena RAG para consultas de trámites
        """
        # Configurar el prompt
        question_prompt = PromptTemplate.from_template(
            """
            sos un asistente virtual de la usina municioal y popular de Tandil, siempre tus respuestas tienen que ser en español. Las mismas tienen que ser de manera amable, concisa y breve
            
            Instrucciones: 

            - En los casos que la respuesta sea muy extensa mostrarlo en forma breve 
            -En caso de falta de informacion podes consultar nuevamente al usuario
            -No podras responder preguntas que sean de la historia de la usina ni la manera de organizarse. 

            Contexto:
            ---------------------
            {context}
            ---------------------
            
            Tus respuestas deben ser claras y concisas, coherentes con la informacion de tu base de datos
            
            Given the context information and not prior knowledge, answer the query.
            Query: {input}
            Answer:
            """
        )
        
        # Configurar embeddings
        embeddings = HuggingFaceEmbeddings(model_name=self.embed_model)
        
        # Configurar ChromaDB
        chroma_client = chromadb.PersistentClient(path=self.db_path)
        
        # Crear vector store
        vectorstore = Chroma(
            client=chroma_client,
            collection_name=self.collection_name,
            embedding_function=embeddings
        )
        
        # Crear retriever
        retriever = vectorstore.as_retriever(k=self.top_k)
        
        # Configurar modelo de lenguaje
        model = ChatOpenAI(model=self.model_name, temperature=0)
        
        # Crear cadena de pregunta-respuesta
        question_answer_chain = create_stuff_documents_chain(model, question_prompt)
        
        # Crear cadena RAG completa
        self.rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    def consultar(self, pregunta):
        """
        Consulta sobre trámites y devuelve una respuesta
        
        Args:
            pregunta (str): La pregunta del usuario sobre trámites
            
        Returns:
            str: Respuesta a la consulta
        """
        try:
            response = self.rag_chain.invoke({"input": pregunta})
            return response["answer"]
        except Exception as e:
            return f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}"


# Ejemplo de uso
if __name__ == "__main__":
    consultor = ConsultorTramites()
    
    while True:
        pregunta = input("Ingresa tu pregunta sobre trámites (o 'salir' para terminar): ")
        if pregunta.lower() == 'salir':
            break
            
        respuesta = consultor.consultar(pregunta)
        print(respuesta)
        