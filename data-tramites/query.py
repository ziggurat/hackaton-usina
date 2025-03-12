import chromadb

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain

load_dotenv()

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