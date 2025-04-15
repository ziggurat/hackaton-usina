import chromadb

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain


# load_dotenv()
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import sys

ENV_PATH = Path('.') / 'usina.env'

print("Loading environment variables from:", ENV_PATH.resolve())

result = load_dotenv(dotenv_path=ENV_PATH.resolve(), override=True)
# print("Reading OPENAI config:", ENV_PATH.resolve(), result)
os.environ["OPENAI_MODEL_NAME"] =  os.getenv('LLM_MODEL') # 'gpt-4o-mini'
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["EMBEDDINGS_MODEL"] = os.getenv("EMBEDDINGS_MODEL")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
print(os.environ["OPENAI_MODEL_NAME"])
print(os.environ["EMBEDDINGS_MODEL"])


EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
QUESTION_PROMPT = PromptTemplate.from_template(
    """
    Context information is below.
    ---------------------
    {context}
    ---------------------
    Given the context information and not prior knowledge, answer the query.
    Query: {input}
    Answer:
    """
)

TOP_K = 3

# Instantiate the embeddings object
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)  # Added embeddings instantiation

# Initialize a ChromaDB client
chroma_client = chromadb.PersistentClient(path="./tramites_db")

# Create a vector store with the embedding function
vectorstore = Chroma(
    client=chroma_client,
    collection_name="tramites",
    embedding_function=embeddings
)

# Create a retriever from the vector store
retriever = vectorstore.as_retriever(k=TOP_K)

# Initialize the language model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Create the question-answering chain
question_answer_chain = create_stuff_documents_chain(model, QUESTION_PROMPT)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

def main():
    while True:
        question = input("Please enter your question (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        
        response = rag_chain.invoke({"input": question})
        
        print(response["answer"])

if __name__ == "__main__":
    main()