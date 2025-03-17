from typing_extensions import Annotated, TypedDict
from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar el modelo de lenguaje
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# Conectar a la base de datos SQLite
db = SQLDatabase.from_uri("sqlite:///usina.db")


class State(TypedDict):
    """Estructura de datos para manejar el flujo de la consulta."""
    question: str
    query: str
    result: str
    answer: str


class QueryOutput(TypedDict):
    """Consulta SQL generada."""
    query: Annotated[str, ..., "Consulta SQL válida sintácticamente."]


class QueryProcessor:
    """Clase para manejar la generación, ejecución y respuesta de consultas SQL."""

    def __init__(self):
        """Inicializa el procesador de consultas."""
        self.db = db
        self.llm = llm

    def write_query(self, state: State) -> str:
        """Genera una consulta SQL a partir de una pregunta en lenguaje natural."""
        query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

        prompt = query_prompt_template.invoke(
            {
                "dialect": self.db.dialect,
                "top_k": 10,
                "table_info": self.db.get_table_info(),
                "input": state["question"],
            }
        )
        structured_llm = self.llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        state["query"] = result["query"]
        return state["query"]

    def execute_query(self, state: State) -> str:
        """Ejecuta la consulta SQL generada y devuelve el resultado."""
        try:
            result = self.db.execute_query(state["query"])
            state["result"] = str(result)
            return state["result"]
        except Exception as e:
            return f"Error ejecutando la consulta: {e}"

    def generate_answer(self, state: State) -> str:
        # Instrucciones de privacidad para el asistente
        privacy_instructions = """
          Tu rol es ser un asistente para consultas internas sobre empleados y temas relacionados con la usina.
          Si la pregunta no está relacionada con la usina o con la información interna de la empresa, responde:
          "Lo siento, pero no tengo información sobre ese tema. Puedo ayudarte con trámites, consultas administrativas o información sobre la historia de la usina."
        """

        # Restricciones implícitas para el formato de respuesta:
        # - Para preguntas sobre cargos y ubicaciones, la respuesta debe centrarse en identificar roles principales y sus áreas en el edificio.
        #   (Ejemplo: listar el cargo seguido de la sección sin detalles superfluos.)
        # - En consultas sobre la ubicación de un empleado, debe describirse brevemente el método o integración que usa el sistema para ubicarlo.
        # - Al presentar datos personales, se debe mostrar información autorizada (por ejemplo, el correo institucional) y omitir datos sensibles.
        # - Para preguntas sobre liderazgo departamental, se debe responder con información jerárquica precisa.
        # - Las respuestas que involucren integración y actualización de datos deben reflejar la dinamización de la información interna.
        #
        # Nota: Estas pautas deben guiar la respuesta según el contexto de la consulta sin ser mencionadas textualmente.
        additional_instructions = """
          Al contestar, utiliza un formato que refleje:
          • Roles y ubicaciones relevantes para la consulta sobre cargos.
          • Breve descripción del proceso interno para determinar ubicaciones.
          • Visualización parcial de datos personales, respetando la privacidad.
          • Información jerárquica precisa en caso de consultar responsables o jefaturas.
          • Indicadores de integración y actualización dinámica para la información interna.
        """

        prompt = (
            f"{privacy_instructions}\n\n"
            f"{additional_instructions}\n\n"
            "Sigue las instrucciones anteriores al pie de la letra.\n\n"
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question:\n\n"
            f"Question: {state['question']}\n"
            f"SQL Query: {state['query']}\n"
            f"SQL Result: {state['result']}"
        )
        response = self.llm.invoke(prompt)
        state["answer"] = response.content
        return state["answer"]

    def process(self, query: str) -> str:
        """Procesa una consulta completa desde la pregunta hasta la respuesta final."""
        state: State = {"question": query, "query": "", "result": "", "answer": ""}
        self.write_query(state)
        self.execute_query(state)
        return self.generate_answer(state)