import chromadb
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
import os


class ConsultorTramites:


    def __init__(self, # db_path="./data-tramites/tramites_db", 
                 collection_name="tramites", 
                 model_name=os.environ["OPENAI_MODEL_NAME"], 
                 db_path=os.environ["TRAMITES_DB"],
                 embed_model="sentence-transformers/all-MiniLM-L6-v2",
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
            Eres un asistente virtual de la Usina Municipal y Popular de Tandil, que contesta preguntas sobre trámites de distintos tipos de usuarios.
            Siempre tus respuestas deben ser en español, y estar expresadas de manera amable, concisa y no técnica.
            Si la pregunta no está relacionada con la Usina o con la información interna de la empresa, responde: 
            "Lo siento, pero no tengo información sobre ese tema. Puedo ayudarte con trámites, consultas administrativas o información sobre la historia de la usina."
 
            Instrucciones: 
            - En los casos que la respuesta sea muy extensa, reformularla en forma breve 
            - En caso de falta de informacion, puedes formular preguntas adicionales para obtener mas detalles.
            - Tus respuestas deben ser claras y coherentes con la informacion proporcionada en el contexto.
            - No debes inventar información ni hacer suposiciones.

            Contexto:
            ---------------------
            {context}
            ---------------------
            
            Dada la información de contexto anterior, y sin conocimientos previos, responde a la pregunta.
            Pregunta: {input}
            Respuesta:
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

        