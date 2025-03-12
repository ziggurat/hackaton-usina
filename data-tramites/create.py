from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import os
from pathlib import Path
from tempfile import mkdtemp

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_docling.loader import ExportType
from langchain_chroma import Chroma
from langchain_docling import DoclingLoader
from docling.chunking import HybridChunker

from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb

load_dotenv()

FILE_PATH = ["documents/tramites.pdf"]
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

EXPORT_TYPE = ExportType.MARKDOWN

QUESTION = "Como doy de baja la electricidad?"
PROMPT = PromptTemplate.from_template(
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

loader = DoclingLoader(
    file_path=FILE_PATH,
    export_type=EXPORT_TYPE,
    chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
)

docs = loader.load()

if EXPORT_TYPE == ExportType.DOC_CHUNKS:
    splits = docs
elif EXPORT_TYPE == ExportType.MARKDOWN:
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ],
    )
    splits = [split for doc in docs for split in splitter.split_text(
        doc.page_content)]
else:
    raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")

# Initialize a ChromaDB client with the new configuration
chroma_client = chromadb.PersistentClient(path="./tramites_db")

vectorstore = Chroma.from_documents(
    client=chroma_client,
    documents=splits,
    embedding=HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID),
    collection_name="tramites"
)

retriever = vectorstore.as_retriever(k=TOP_K)

model = ChatOpenAI(model="gpt-4o", temperature=0)

question_answer_chain = create_stuff_documents_chain(model, PROMPT)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

response = rag_chain.invoke({"input": QUESTION})

print(response["answer"])
