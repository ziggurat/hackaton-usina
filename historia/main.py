from dotenv import load_dotenv
load_dotenv()


import fitz  # pip install pymupdf

import numpy as np
from shapely.geometry import box
import pandas as pd

import io

from shapely.geometry import box
from shapely.ops import unary_union
import os
from collections import defaultdict

import pytesseract
from PIL import Image
from collections import defaultdict

from tqdm import tqdm

import pickle

import numpy as np

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

from chromadb.utils.data_loaders import ImageLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings

from operator import itemgetter

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI



class IngestionPipeline:
    
    def __init__(self, create=True):
        self.dir_path = os.environ.get('OUTPUT_PATH')
        
        # set default text and image embedding functions
        self.embedding_function = OpenCLIPEmbeddingFunction()
        self.chroma_collection = self.create_vector_store(create=create)

    
    def create_vector_store(self, create=True):
        db_dir = os.environ.get('DB_NAME')
        collection_name = os.environ.get('COLLECTION_NAME')
        
        db_name = self.dir_path + db_dir

        if not os.path.exists(db_name):
            print("Creating vector store: ", db_name)
            os.mkdir(db_name)
        else:
            print("Updating vector store:", db_name)

        # create client and a new collection
        self.chroma_client = chromadb.PersistentClient(path=db_name, settings=Settings(allow_reset=True))
        image_loader = ImageLoader()

        if create:
            print("Deleting existing collection ...")
            self.chroma_client.reset()
            print("Creating new collection ...")
            chroma_collection = self.chroma_client.get_or_create_collection(
                collection_name, metadata={"hnsw:space": "cosine"},
                embedding_function=self.embedding_function,
                data_loader=image_loader
            )
        else:
            print("Recovering existing collection ...")
            chroma_collection = self.chroma_client.get_or_create_collection(
                collection_name, metadata={"hnsw:space": "cosine"},
                embedding_function=self.embedding_function,
                data_loader=image_loader
            )
            print("elements:", chroma_collection.count())

        return chroma_collection

    @staticmethod
    def are_rectangles_connected(rect1, rect2, threshold=0):
        """
        Check if two rectangles are connected (overlap or close within a threshold).
        
        :param rect1: Tuple (x1, y1, x2, y2) for the first rectangle.
        :param rect2: Tuple (x1, y1, x2, y2) for the second rectangle.
        :param threshold: Minimum distance to consider rectangles as connected.
        :return: True if connected, False otherwise.
        """
        b1 = box(*rect1).buffer(threshold)  # Expand rect1 by threshold
        b2 = box(*rect2)
        return b1.intersects(b2)

    @staticmethod
    def group_connected_rectangles(rectangles, threshold=0):
        """
        Group rectangles into clusters based on connectivity.
        
        :param rectangles: List of rectangles [(x1, y1, x2, y2), ...]
        :param threshold: Distance threshold to consider rectangles connected.
        :return: List of grouped rectangles as [(grouped_x1, grouped_y1, grouped_x2, grouped_y2), ...]
        """
        n = len(rectangles)
        adjacency_matrix = np.zeros((n, n), dtype=bool)
        
        # Build adjacency matrix
        for i in range(n):
            for j in range(i + 1, n):
                if IngestionPipeline.are_rectangles_connected(rectangles[i], rectangles[j], threshold):
                    adjacency_matrix[i, j] = True
                    adjacency_matrix[j, i] = True
        
        # Find connected components
        visited = [False] * n
        groups = []
        
        def dfs(node, group):
            visited[node] = True
            group.append(node)
            for neighbor in range(n):
                if adjacency_matrix[node, neighbor] and not visited[neighbor]:
                    dfs(neighbor, group)
        
        for i in range(n):
            if not visited[i]:
                group = []
                dfs(i, group)
                groups.append(group)
        
        # Merge rectangles within each group
        grouped_rectangles = []
        for group in groups:
            x_min = min(rectangles[i][0] for i in group)
            y_min = min(rectangles[i][1] for i in group)
            x_max = max(rectangles[i][2] for i in group)
            y_max = max(rectangles[i][3] for i in group)
            grouped_rectangles.append((x_min, y_min, x_max, y_max))
        
        return grouped_rectangles
    
    @staticmethod
    def stitch_grouped_images_with_dpi(image_data, image_coords, grouped_boxes, dpi=300):
        """
        Stitch images together for each grouped bounding box, preserving size and quality.
        
        :param image_data: List of image bytes.
        :param image_coords: List of tuples [(x1, y1, x2, y2)], coordinates of the images in the PDF.
        :param grouped_boxes: List of grouped bounding boxes [(group_x1, group_y1, group_x2, group_y2)].
        :param dpi: DPI value to scale the images correctly.
        :return: List of stitched PIL.Image objects, one for each group.
        """
        # Scale factor to convert coordinates to pixels
        scale = dpi / 72  # 72 is the default DPI in PDFs
        
        stitched_images = []
        
        for group_box in grouped_boxes:
            # Scale group box dimensions to pixels
            group_x1, group_y1, group_x2, group_y2 = group_box
            canvas_width = int((group_x2 - group_x1) * scale)
            canvas_height = int((group_y2 - group_y1) * scale)
            
            # Create a blank canvas for the group
            canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
            
            for img_bytes, coords in zip(image_data, image_coords):
                # Convert image bytes to PIL.Image
                img = Image.open(io.BytesIO(img_bytes))
                
                # Check if this image belongs to the current group
                img_x1, img_y1, img_x2, img_y2 = coords
                if (
                    group_x1 <= img_x1 < group_x2 and group_y1 <= img_y1 < group_y2
                    or group_x1 <= img_x2 <= group_x2 and group_y1 <= img_y2 <= group_y2
                ):
                    # Scale image coordinates to pixels
                    paste_x = int((img_x1 - group_x1) * scale)
                    paste_y = int((img_y1 - group_y1) * scale)
                    img_width = int((img_x2 - img_x1) * scale)
                    img_height = int((img_y2 - img_y1) * scale)
                    
                    # Resize only if necessary, using high-quality resampling
                    if img.size != (img_width, img_height):
                        img = img.resize((img_width, img_height), resample=Image.Resampling.LANCZOS)
                    
                    # Paste the image onto the canvas
                    canvas.paste(img, (paste_x, paste_y), img if img.mode == 'RGBA' else None)
            
            stitched_images.append(canvas)
    
        return stitched_images
    
    
    def _process_pdf_pages(self, pdf_filename:str, images_dir='images'):

        file = self.dir_path + pdf_filename
        print("Processing PDF pages: "+file)
        
        dict_mapping_pages = defaultdict(list)

        # open the file
        pdf_file = fitz.open(file)

        # iterate over PDF pages
        for page_index in range(len(pdf_file)):

            # get the page itself
            page = pdf_file.load_page(page_index)  # load the page
            image_list = page.get_images(full=True)  # get images on the page

            # printing number of images found in this page
            if image_list:
                print(f"[+] Found a total of {len(image_list)} images on page {page_index}")
            else:
                print("[!] No images found on page", page_index)
            
            image_data = []
            image_coords = []
            for image_index, img in enumerate(image_list, start=1):
                # get the XREF of the image
                xref = img[0]

                # extract the image bytes
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]

                # get the image extension
                image_ext = base_image["ext"]

                img_rect = page.get_image_rects(xref)[0]
                coords = (img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1)

                # print(page_index+1,image_index,coords)

                image_data.append(image_bytes)
                image_coords.append(coords)

            grouped_boxes = IngestionPipeline.group_connected_rectangles(image_coords, threshold=0)

            # print(grouped_boxes)

            stitched_images = IngestionPipeline.stitch_grouped_images_with_dpi(image_data, image_coords, grouped_boxes)

            # Save or display the stitched images

            if not os.path.exists(self.dir_path + images_dir):
                os.mkdir(self.dir_path + images_dir)

            for i, img in enumerate(stitched_images):
                fname =  self.dir_path+images_dir+'/stitched_group_'+str(page_index+1)+'_'+str(i)+'.png'
                print('Saving... ', fname)
                img.save(fname)
                dict_mapping_pages[page_index+1].append(f'stitched_group_{page_index+1}_{i}')
            
        return dict_mapping_pages
    
    @staticmethod
    def load_image(infilename): # Read image from file system and convert it to numpy array
        img = Image.open( infilename )
        img.load()
        data = np.asarray(img, dtype="int32")
        return data

    def _extract_paragraphs(self, pdf_filename:str, header_height=140, footer_height=158):
        file = self.dir_path + pdf_filename

        print("Extracting paragraphs: "+file)
        doc = fitz.open(file)

        dict_extracted_paragraphs = defaultdict(list)

        # header_height = 140 # manually defined
        # footer_height = 158

        # Iterate over the pages of the PDF
        for page_num in tqdm(range(len(doc)), "pages"):
        # for page_num in range(len(doc)):

            # print("-"*10, page_num)

            page = doc.load_page(page_num)  # Load the page
            
            # Convert the page to an image (pixmap)
            pix = page.get_pixmap()

            # Increase resolution by scaling the page (2x in this case)
            matrix = fitz.Matrix(2, 2)  # Scaling by a factor of 2
            pix = page.get_pixmap(matrix=matrix)  # Convert page to high-res image

            # Convert to Pillow Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            width, height = img.size
            img = img.crop((0, header_height, width, height - footer_height))
            
            # Apply Tesseract OCR to the image
            text = pytesseract.image_to_string(img)

            # Print out the extracted text
            # print(f"Text from page {page_num + 1}:\n{text}\n")
            dict_extracted_paragraphs[page_num + 1].append(text.replace('\n',''))
            # print('='*10)
        
        return dict_extracted_paragraphs
    
    def _ingest_images(self, images_dir):
        print("Adding images to vector store ...")
        for page, images in self.dict_mapping_pages.items():
            for im in images:
                image_name = self.dir_path + images_dir + im + '.png'  # TODO: Fix name if necessary
                if os.path.exists(image_name): 
                    log_info = {
                        "ids": [im],
                        "uris": [image_name],
                        "metadatas": [{'page': page, 'type': 'image'}]
                    }
                    print("LOG (Image):", log_info)
                    
                    # NOTE: si o si hay que agregar el documents porque sino la class Document explota cuando hacemos
                    # busquedas porque falta ese field.
                    # En algun momento se guardo el base64 de la image, pero no tiene mucho sentido ya que con el uris
                    # podemos recuperar la imagen original si es necesario.
                    
                    self.chroma_collection.add(
                        ids=[im],
                        uris=[image_name],
                        metadatas=[{'page': page, 'type': 'image'}]
                    )
    
    def _ingest_text(self):
        print("Adding text to vector store ...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
        for page, paragraphs in self.dict_extracted_paragraphs.items():
            total_chunks = 0
            for i in range(len(paragraphs)):
                chunked_documents = text_splitter.split_text(paragraphs[i]) 
                total_chunks += len(chunked_documents)
                for j in range(len(chunked_documents)):
                    log_info = {
                        "ids": [f'paragraph_{page}_{i}_{j}'],
                        "documents": [chunked_documents[j]],
                        "metadatas": [{'page': page, 'paragraph': i, 'chunk': j, 'type': 'text'}]
                    }
                    print("LOG (Text):", log_info)
                    self.chroma_collection.add(
                        ids=[f'paragraph_{page}_{i}_{j}'],
                        documents=[chunked_documents[j]],
                        metadatas=[{'page': page, 'paragraph': i, 'chunk': j, 'type': 'text'}]
                    )
            print("page:", page, "paragraphs:", len(paragraphs), "chunks:", total_chunks)

    
    def process_pdf(self, pdf_filename:str=None, pickle_filename: str='dicts_images_text.pickle', reload=False, images_dir='images/'):
        
        if (pdf_filename is not None) and (not reload):
            self.dict_mapping_pages = self._process_pdf_pages(pdf_filename)
            self.dict_extracted_paragraphs = self._extract_paragraphs(pdf_filename)
            with open(self.dir_path + pickle_filename, 'wb') as file:
                pickle.dump([self.dict_mapping_pages,self.dict_extracted_paragraphs],file)
        else:
            self.dict_mapping_pages, self.dict_extracted_paragraphs = pd.read_pickle(self.dir_path + pickle_filename)

        # Persist images in vector store
        self._ingest_images(images_dir)
        # Persist text in vector store
        self._ingest_text()

    
    def get_vector_store_collection(self):
        return self.chroma_collection
    
    def get_vector_store_client(self):
        return self.chroma_client

pipeline = IngestionPipeline(create=False)
pipeline.process_pdf(pdf_filename='historiausina.pdf')
