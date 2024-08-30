import os
import uuid
from typing import Callable, Iterable, List, Optional, Union

import chromadb
from chromadb import config
from chromadb.utils import embedding_functions

from app.vectorstore import VectorStore
from app.config import settings


DEFAULT_EMBEDDING_FUNCTION = embedding_functions.DefaultEmbeddingFunction()


class ChromaDB(VectorStore):
    """
    Implementation of ChromeDB vector store
    """

    def __init__(
        self,
        collection_name: str = "bamboo-etl",
        embedding_function: Optional[Callable[[List[str]], List[float]]] = None,
        persist_path: Optional[str] = None,
        client_settings: Optional[config.Settings] = None,
        max_samples: int = 3,
        similary_threshold: int = 1.5,
    ) -> None:
        self._max_samples = max_samples
        self._similarity_threshold = similary_threshold

        # Initialize Chromadb Client
        # initialize from client settings if exists
        if client_settings:
            client_settings.persist_directory = (
                persist_path or client_settings.persist_directory
            )
            _client_settings = client_settings

        # use persist path if exists
        elif persist_path:
            _client_settings = config.Settings(
                is_persistent=True, anonymized_telemetry=False
            )
            _client_settings.persist_directory = persist_path
        # else use root as default path
        else:
            _client_settings = config.Settings(
                is_persistent=True, anonymized_telemetry=False
            )
            _client_settings.persist_directory = settings.chromadb_url

        self._client_settings = _client_settings
        self._client = chromadb.Client(_client_settings)
        self._persist_directory = _client_settings.persist_directory

        self._embedding_function = embedding_function or DEFAULT_EMBEDDING_FUNCTION

        self._docs_collection = self._client.get_or_create_collection(
            name=collection_name, embedding_function=self._embedding_function
        )

    def add_docs(
        self,
        docs: Iterable[str],
        ids: Optional[Iterable[str]] = None,
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Add docs to the training set
        Args:
            docs: Iterable of strings to add to the vectorstore.
            ids: Optional Iterable of ids associated with the texts.
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        if ids is None:
            ids = [f"{str(uuid.uuid4())}-docs" for _ in docs]

        self._docs_collection.add(
            documents=docs,
            metadatas=metadatas,
            ids=ids,
        )

    def delete_docs(
        self, ids: Optional[List[str]] = None, metadata_criteria: Optional[dict] = None
    ) -> Optional[bool]:
        """
        Delete by vector ID to delete docs
        Args:
            ids: List of ids to delete

        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise
        """

        if ids is None and metadata_criteria is not None:
            records_to_delete = self._docs_collection.get(where=metadata_criteria)
            ids = [record["id"] for record in records_to_delete]

        self._docs_collection.delete(ids=ids)
        return True

    def get_relevant_docs(self, question: str, k: int = None) -> List[dict]:
        """
        Returns relevant documents based search
        """
        k = k or self._max_samples

        relevant_data: chromadb.QueryResult = self._docs_collection.query(
            query_texts=question,
            n_results=k,
            include=["metadatas", "documents", "distances"],
        )

        return self._filter_docs_based_on_distance(
            relevant_data, self._similarity_threshold
        )

    def get_relevant_docs_documents(self, question: str, k: int = None) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        return self.get_relevant_docs(question, k)["documents"][0]

    def _filter_docs_based_on_distance(
        self, documents: chromadb.QueryResult, threshold: int
    ) -> List[str]:
        """
        Filter documents based on threshold
        Args:
            documents (List[str]): list of documents in string
            distances (List[float]): list of distances in float
            threshold (int): similarity threshold

        Returns:
            _type_: _description_
        """
        filtered_data = [
            (doc, distance, metadata, ids)
            for doc, distance, metadata, ids in zip(
                documents["documents"][0],
                documents["distances"][0],
                documents["metadatas"][0],
                documents["ids"][0],
            )
            if distance < threshold
        ]

        return {
            key: [[data[i] for data in filtered_data]]
            for i, key in enumerate(["documents", "distances", "metadatas", "ids"])
        }