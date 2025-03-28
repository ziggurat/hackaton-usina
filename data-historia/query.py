from chromadb.utils.data_loaders import ImageLoader
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

    print("data dict question: " + data_dict['question'])

    text_message_initial = {
        "type": "text",
        "text": (
            "Como experto en preguntas analiza si la pregunta realizada es directa o si es abierta. "
            "Una pregunta directa pide datos concretos. Una pregunta abierta requiere contexto, análisis histórico, resúmenes, comparativas.\n"
            "- Decidir si la pregunta del usuario es directa o abierta.\n"
            #"Clasifica la pregunta en una de las siguientes categorías:\n"
            #"- Pregunta directa: Pregunta que no necesita de contexto adicional para ser respondida.\n"
            #"- Pregunta abierta: Pregunta que necesita de contexto adicional para ser respondida.\n"
            "Instrucciones:\n"
            "- NO incluyas el tipo de pregunta en la respuesta."
        )
    }
    messages.append(text_message_initial)
    initial_response = [HumanMessage(content=messages)]

    #print("initial response: \n")
    #print(initial_response)
    #print("\n")

    # Adding the text message for analysis
    text_message = {
        "type": "text",
        "text": (
            "Como historiador experto y particularmente en la historia de la Usina de Tandil, tu tarea es analizar e interpretar textos e imágenes "
            "considerando su importancia histórica y cultural. Ambos se recuperarán de una vectorstore basada "
            "en las palabras clave ingresadas por el usuario. Utiliza tu amplio conocimiento y habilidades analíticas para proporcionar una "
            "respuesta analizando los chunks minuciosamente y filtrando información similar dependiendo el contexto histórico y cronológico.\n"
            #f"La pregunta del usuario es: {initial_response}\n"
            "Si la pregunta es abierta haz lo siguiente:\n"
            "- Responde la pregunta entre 300 y 1000 caracteres.\n"
            "- El contexto histórico y cultural del texto (si corresponde).\n"
            "- Conexiones entre el texto y la imagen (si la hay).\n"
            
            "Si la pregunta es concisa haz lo siguiente:\n"
            "- Responde la pregunta en no más de 300 caracteres.\n"
            "Instrucciones:\n"
            "- Evalúa la cronología de los eventos para contrastar hechos y fechas correctamente.\n"
            "- Brinda tu respuesta en español.\n"
            "- Trae una única imagen.\n"
            "- La respuesta NO debe incluir el análisis previo.\n"
            "- NO INVENTES. Limitate estrictamente al contexto proporcionada.\n"
            f"Palabras clave proporcionadas por el usuario: {data_dict['question']}\n\n"
            "Texto y/o tablas:\n"
            f"{formatted_texts}"
        ),
    }
    messages.append(text_message)
    final_response = [HumanMessage(content=messages)]

    #final_response.pop(0)
    #print("final response: \n")
    #print(final_response)
    #print("\n")

    return final_response


def plt_img_base64(img_base64):
    # Decode the base64 image and display using streamlit
    img_bytes = base64.b64decode(img_base64)
    #st.image(img_bytes)


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



def inspect_collection():
    """Helper function to directly inspect the ChromaDB collection"""

    print("## Collection Inspection")

    try:
        # Get raw collection data
        collection = chroma_client.get_collection(
            name=collection_name, data_loader=ImageLoader())
        count = collection.count()
        print(f"Total documents: {count}")

        if count > 0:
            # Get a sample of docs from ChromaDB directly
            sample = collection.get(limit=5, include=["metadatas", "uris", "data"], where={
                                    "type": {"$eq": "image"}})

            if 'data' in sample:
                print("### Image Data")
                for i, data in enumerate(sample['data']):
                    print(f"Image {i+1}:")
                    #st.image(data)

            if 'uris' in sample:
                print("### Image URIs")
                for i, uris in enumerate(sample['uris']):
                    print(f"URIs for image {i+1}: {uris}")

            if 'metadatas' in sample:
                print("### Image Metadata")
                for i, metadata in enumerate(sample['metadatas']):
                    print(f"Metadata for image {i+1}:")
                    #st.json(metadata)

    except Exception as e:
        print(f"Error inspecting collection: {e}")
        #st.code(traceback.format_exc())


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
    print("Base de datos de la historia de la Usina de Tandil")

    # Call this function in your main code
    # inspect_collection()

    # Query input via Streamlit
    query = input("Preguntá algo:")

    # Initialize a set to store unique page numbers
    pages_found = set()

    if query:
        docs = create_text_retriever().invoke(query, k=6)

        if (len(docs) == 0):
            print("No hay resultados")

        for doc in docs:
            # accumulate unique page numbers
            page = doc.metadata.get('page')
            if page is not None:
                pages_found.add(page)
            print("\n")
            print(doc.page_content)

        # Safely retrieve images with error handling
        try:
            # Skip image retrieval if no pages were found
            if not pages_found:
                print("### No pages found to retrieve related images")
            else:
                print(
                    f"Searching for images on pages: {', '.join(str(p) for p in pages_found)}")

                #get_and_display_sample_images(list(pages_found), limit=5)

        except Exception as e:
            error_msg = f"Error retrieving images: {e}"
            trace = traceback.format_exc()
            print(error_msg)
            #st.code(trace)  # Display stack trace in a code block in Streamlit
            print(error_msg)
            print(trace)

    response = chain.invoke(query)
    print("\n")
    print("RESPUESTA FINAL GENERADA:")
    print("\n")
    print(response)


if __name__ == "__main__":
    main()
