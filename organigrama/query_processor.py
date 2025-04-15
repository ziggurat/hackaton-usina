from typing_extensions import Annotated, TypedDict
from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
import os

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

        # Inicializar el modelo de lenguaje
        self.llm = init_chat_model(os.environ["LLM_MODEL"], model_provider="openai")

        # Conectar a la base de datos SQLite
        self.db = SQLDatabase.from_uri(os.environ["ORGANIGRAMA_DB"])
        # print(self.db.get_usable_table_names())

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
            result = self.db.run(state["query"])
            state["result"] = str(result)
            return state["result"]
        except Exception as e:
            return f"Error ejecutando la consulta: {e}"

    def generate_answer(self, state: State) -> str:
        # Instrucciones de privacidad para el asistente
        privacy_instructions = """
          Eres un asistente para consultas internas sobre empleados y áreas relacionadas con la Usina Popular y Municipal de Tandil.
          Siempre tus respuestas deben ser en español, y estar expresadas de manera amable, concisa y no técnica.
          Si la pregunta no está relacionada con la Usina o con la información interna de la empresa, responde:
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
          Al elaborar tu respuesta, utiliza un formato que refleje:
          • Roles y ubicaciones relevantes para la consulta sobre cargos.
          • Breve descripción del proceso interno para determinar ubicaciones.
          • Provisión parcial de datos personales, respetando la privacidad.
          • Información jerárquica precisa en caso de consultar responsables o jefaturas.
          • Indicadores de integración y actualización dinámica para la información interna.
        """

        prompt = (
            f"{privacy_instructions}\n\n"
            f"{additional_instructions}\n\n"
            "Sigue las instrucciones anteriores al pie de la letra.\n\n"
            "Dada la siguiente pregunta del usuario, su consulta SQL correspondiente, "
            "y el resultado de la consulta SQL, responde a la pregunta.\n"
            "No debes inventar información ni hacer suposiciones.\n\n"
            f"Pregunta: {state['question']}\n"
            f"Consulta SQL: {state['query']}\n"
            f"Resultado de Consulta SQL: {state['result']}\n"
            "Respuesta:"
        )
        response = self.llm.invoke(prompt)
        state["answer"] = response.content
        return state["answer"]

    def consultar(self, query: str) -> str:
        """Procesa una consulta completa desde la pregunta hasta la respuesta final."""
        state: State = {"question": query, "query": "", "result": "", "answer": ""}
        query = self.write_query(state)
        result = self.execute_query(state)
        # print(query)
        # print(result)
        if len(result) > 0:
            return self.generate_answer(state)
        else: 
            return "No se encontraron resultados para la consulta."


