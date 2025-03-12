from typing_extensions import Annotated, TypedDict
from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from dotenv import load_dotenv  # added import for dotenv
load_dotenv()  # load environment variables from .env


llm = init_chat_model("gpt-4o-mini", model_provider="openai")
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")
db = SQLDatabase.from_uri("sqlite:///usina.db")


class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str


class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    """Generate SQL query to fetch information."""

    query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return result["query"]


def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return execute_query_tool.invoke(state["query"])


def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return response.content

state = State()
state["question"] = input("Enter your question: ")
state["query"] = write_query(state)
state["result"] = execute_query(state)
state["answer"] = generate_answer(state)

print(state["answer"])