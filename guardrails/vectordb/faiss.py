from typing import List, Optional

from guardrails.embedding import EmbeddingBase
from guardrails.vectordb.base import VectorDBBase

try:
    import faiss
    from faiss import Index

except ImportError:
    pass

faiss_error = (
    "`faiss` is required for using vectordb.faiss."
    "Install it with `poetry add faiss-cpu`."
)


class Faiss(VectorDBBase):
    def __init__(
        self, index: "Index", embedder: EmbeddingBase, path: Optional[str] = None
    ) -> None:
        try:
            import faiss  # noqa: F401
        except ImportError:
            raise ImportError(faiss_error)

        super().__init__(embedder, path)
        self._index = index

    @classmethod
    def new_flat_l2_index(
        cls, vector_dim: int, embedder: EmbeddingBase, path: Optional[str] = None
    ):
        pass

    @classmethod
    def new_flat_ip_index(
        cls, vector_dim: int, embedder: EmbeddingBase, path: Optional[str] = None
    ):
        pass

    @classmethod
    def new_flat_l2_index_from_embedding(
        cls,
        embedding: List[List[float]],
        embedder: EmbeddingBase,
        path: Optional[str] = None,
    ):
        pass

    @classmethod
    def load(cls, path: str, embedder: EmbeddingBase):
        if faiss is None:
            raise ImportError(faiss_error)

        index = faiss.read_index(path)
        return cls(index, embedder, path)

    def save(self, path: Optional[str] = None):
        pass

    def similarity_search_vector(self, vector: List[float], k: int) -> List[int]:
        import numpy as np

        # FIXME is this correct usage of `search`?
        #  Arguments missing for parameters "k", "distances", "labels"
        _, scores = self._index.search(np.array([vector]), k)  # type: ignore
        return scores[0].tolist()

    def similarity_search_vector_with_threshold(
        self, vector: List[float], k: int, threshold: float
    ) -> List[int]:
        pass

    def add_vectors(self, vectors: List[List[float]]) -> None:
        pass

    def last_index(self) -> int:
        pass
