import os
import uuid
from typing import List, Dict, Any
import re
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from loguru import logger
from qdrant_client.models import Distance, VectorParams, PointStruct

from src.common_aidevs.files_read_write_download import read_txt_file

load_dotenv()
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")


def openai_get_embedding(text: str, model: str = "text-embedding-3-small"):
    client = OpenAI()
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


class ThinQdrantClient:
    def __init__(self):
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )

    def qdrant_create_collection(
        self, collection_name: str, size: int = 1536, distance=Distance.COSINE
    ):
        existing_collections: List[str] = [
            col.name for col in self.client.get_collections().collections
        ]
        if collection_name not in existing_collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=size, distance=distance),
            )
            logger.debug(f"Successfully created collection: {collection_name}")
        else:
            logger.debug(f"Collection: {collection_name} already exists.")

    def qdrant_upsert(
        self,
        collection_name: str,
        unique_id: str,
        embedding: List[float],
        payload: Dict[str, Any],
    ):
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[PointStruct(id=unique_id, vector=embedding, payload=payload)],
            )
            logger.success(f"Successfully added {unique_id} to {collection_name}.")
        except Exception as e:
            logger.error(f"Error adding {unique_id} to {collection_name}.\n{e}")

    def qdrant_search(
        self, collection_name: str, query_vector: List[float], top_k: int
    ):
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
        )

    def query_similar_text(
        self,
        query_text: str,
        collection_name: str,
        top_k: int = 5,
        embedding_model: str = "text-embedding-3-small",
    ):
        query_vector = openai_get_embedding(query_text, model=embedding_model)
        return self.client.search(
            collection_name=collection_name, query_vector=query_vector, limit=top_k
        )


def embedd_files_in_folder(
    qdrant_client: ThinQdrantClient, folder_path, collection_name: str
):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Process file based on type and get classification
        if filename.endswith(".txt"):
            text = read_txt_file(file_path).strip()
            unique_id = str(uuid.uuid4())
            embedding = openai_get_embedding(text)
            # Extract date using regex
            date_matches = re.findall(r"\d{4}_\d{2}_\d{2}", filename)
            if date_matches:
                date_str = date_matches[0]  # Take the first match
                date_object = datetime.strptime(date_str, "%Y_%m_%d")
                formatted_date = date_object.strftime("%Y-%m-%d")

                qdrant_client.qdrant_upsert(
                    collection_name=collection_name,
                    unique_id=unique_id,
                    embedding=embedding,
                    payload={
                        "file_name": filename,
                        "content": text,
                        "file_date": formatted_date,
                    },
                )


thin_qdrant_client = ThinQdrantClient()
# qdrant_client = QdrantClient(host="localhost", port=6333)
print(thin_qdrant_client.client.get_collections())
COLLECTION = "S03E02_wektors"
thin_qdrant_client.qdrant_create_collection(COLLECTION)
print(thin_qdrant_client.client.get_collections())

# Get paths
base_path = os.getcwd()
print(base_path)
reports_folder = os.path.join(base_path, "do-not-share")
embedd_files_in_folder(thin_qdrant_client, reports_folder, COLLECTION)
question = (
    "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
)
search_result = thin_qdrant_client.query_similar_text(question, COLLECTION)
result_date = search_result[0].payload["file_date"]
logger.info(f"ANSWER: {result_date}")
