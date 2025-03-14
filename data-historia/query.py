from chromadb.utils.data_loaders import ImageLoader
import streamlit as st
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
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

image_loader = ImageLoader()


def resize_base64_image(base64_string, size=(128, 128)):
    """
    Resize an image encoded as a Base64 string.

    Args:
    base64_string (str): Base64 string of the original image.
    size (tuple): Desired size of the image as (width, height).

    Returns:
    str: Base64 string of the resized image.
    """
    # Decode the Base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))

    # Resize the image
    resized_img = img.resize(size, Image.LANCZOS)

    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)

    # Encode the resized image to Base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def is_base64(s):
    """Check if a string is Base64 encoded"""
    try:
        return base64.b64encode(base64.b64decode(s)) == s.encode()
    except Exception:
        return False


def split_image_text_types(docs):
    """Split numpy array images and texts"""
    images = []
    text = []
    for doc in docs:
        doc = doc.page_content  # Extract Document contents
        if is_base64(doc):
            # Resize image to avoid OAI server error
            images.append(
                resize_base64_image(doc, size=(250, 250))
            )  # base64 encoded str
        else:
            text.append(doc)
    return {"images": images, "texts": text}


def prompt_func(data_dict):
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

    # Adding the text message for analysis
    text_message = {
        "type": "text",
        "text": (
            "As an expert historian and particularly in Tandil history, your task is to analyze and interpret text and images, "
            "considering their historical and cultural significance. Provide your response in Spanish. Alongside the images, you will be "
            "provided with related text to offer context. Both will be retrieved from a vectorstore based "
            "on user-input keywords. Please use your extensive knowledge and analytical skills to provide a "
            "comprehensive summary that includes:\n"
            "- A detailed description of your answer.\n"
            "- The historical and cultural context for the text and images (if any).\n"
            "- An interpretation of the image's symbolism and meaning.\n"
            "- Connections between the text and images (if any).\n\n"
            f"User-provided keywords: {data_dict['question']}\n\n"
            "Text and / or tables:\n"
            f"{formatted_texts}"
        ),
    }
    messages.append(text_message)

    return [HumanMessage(content=messages)]


def plt_img_base64(img_base64):
    # Decode the base64 image and display using streamlit
    img_bytes = base64.b64decode(img_base64)
    st.image(img_bytes)


db_path = os.environ.get('OUTPUT_PATH') + os.environ.get('DB_NAME')
collection_name = os.environ.get('COLLECTION_NAME')

chroma_client = chromadb.PersistentClient(path=db_path)
vector_store_from_client = Chroma(
    client=chroma_client,
    collection_name=collection_name,
    embedding_function=OpenCLIPEmbeddings(
        model_name="ViT-B-32", checkpoint="laion2b_s34b_b79k"),
)


def create_text_retriever():
    return vector_store_from_client.as_retriever()


def get_and_display_sample_images(page_nums, limit=5):
    """
    Retrieve and display images using page metadata field from ChromaDB collection
    
    Args:
        collection_name (str): Name of the ChromaDB collection
        page_nums (list): List of page numbers to filter images by
        limit (int): Maximum number of images to retrieve and display
        
    Returns:
        dict: The raw sample data returned from ChromaDB
    """

    #  TODO: Maybe we need a custom retriever for the multimodal collection, interacting directly with ChromaDB for images
    # https://python.langchain.com/docs/how_to/custom_retriever/
    try:
        # Get raw collection data
        collection = chroma_client.get_collection(
            name=collection_name, data_loader=ImageLoader())
        count = collection.count()
        st.write(f"Total documents: {count}")

        sample = None
        if count > 0:
            # Get a sample of docs from ChromaDB directly with specified type
            sample = collection.get(
                limit=limit,
                include=["metadatas", "uris", "data"],
                where={"$and": [
                    {"type": {"$eq": "image"}},
                    {"page": {"$in": page_nums}}
                ]}
            )

            # Display images if available
            if 'data' in sample and sample['data']:
                st.write(f"### Related images")
                for i, data in enumerate(sample['data']):
                    st.write(f"Image {i+1}:")
                    st.image(data)
            else:
                st.write(f"No images found")

        return sample

    except Exception as e:
        st.error(f"Error retrieving images from collection: {e}")
        st.code(traceback.format_exc())
        return None


def inspect_collection():
    """Helper function to directly inspect the ChromaDB collection"""

    st.write("## Collection Inspection")

    try:
        # Get raw collection data
        collection = chroma_client.get_collection(
            name=collection_name, data_loader=ImageLoader())
        count = collection.count()
        st.write(f"Total documents: {count}")

        if count > 0:
            # Get a sample of docs from ChromaDB directly
            sample = collection.get(limit=5, include=["metadatas", "uris", "data"], where={
                                    "type": {"$eq": "image"}})

            if 'data' in sample:
                st.write("### Image Data")
                for i, data in enumerate(sample['data']):
                    st.write(f"Image {i+1}:")
                    st.image(data)

            if 'uris' in sample:
                st.write("### Image URIs")
                for i, uris in enumerate(sample['uris']):
                    st.write(f"URIs for image {i+1}: {uris}")

            if 'metadatas' in sample:
                st.write("### Image Metadata")
                for i, metadata in enumerate(sample['metadatas']):
                    st.write(f"Metadata for image {i+1}:")
                    st.json(metadata)

    except Exception as e:
        st.write(f"Error inspecting collection: {e}")
        st.code(traceback.format_exc())


llm = ChatOpenAI(
    model='o3-mini'
)

# RAG pipeline
chain = (
    {
        "context": create_text_retriever() | RunnableLambda(split_image_text_types),
        "question": RunnablePassthrough(),
    }
    | RunnableLambda(prompt_func)
    | llm
    | StrOutputParser()
)


def main():
    st.title("Base de datos de la historia de la Usina de Tandil")

    # Call this function in your main code
    # inspect_collection()

    # Query input via Streamlit
    query = st.text_input("Preguntá algo:")

    # Initialize a set to store unique page numbers
    pages_found = set()

    if query:
        docs = create_text_retriever().invoke(query, k=3)

        if (len(docs) == 0):
            st.write("No hay resultados")

        for doc in docs:
            # accumulate unique page numbers
            page = doc.metadata.get('page')
            if page is not None:
                pages_found.add(page)

            st.write(doc.page_content)

        # Safely retrieve images with error handling
        try:
            # Skip image retrieval if no pages were found
            if not pages_found:
                st.write("### No pages found to retrieve related images")
            else:
                st.write(
                    f"Searching for images on pages: {', '.join(str(p) for p in pages_found)}")

                get_and_display_sample_images(list(pages_found), limit=5)

        except Exception as e:
            error_msg = f"Error retrieving images: {e}"
            trace = traceback.format_exc()
            st.write(error_msg)
            st.code(trace)  # Display stack trace in a code block in Streamlit
            print(error_msg)
            print(trace)

    # response = chain.invoke(query)
    # st.markdown(response)


if __name__ == "__main__":
    main()
