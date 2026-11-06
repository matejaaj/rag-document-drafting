from app.model.rag.vector_models import ChunkVector, DocumentVector
from app.services.rag.retrieval_models import RetrievalConfig
from app.services.rag.retrieval_service import RetrievalService


class FixedEmbeddings:
    def embed_query(self, text):
        return [0.0]


class KnowledgeBase:
    def __init__(self, documents, chunks):
        self.documents = documents
        self.chunks = chunks

    def search_documents_by_vector(self, *, query_vector, limit, document_type_id):
        return self.documents

    def search_chunks_by_vector(self, *, query_vector, limit, document_ids):
        return [row for row in self.chunks if row[0].document_id in document_ids]


def document(document_id, distance):
    return DocumentVector(id=document_id, storage_object_id=1, document_type_id=1), distance


def chunk(document_id, index, text, distance, section_name="Opšte"):
    return ChunkVector(
        id=f"{document_id}-{index}", document_id=document_id, storage_object_id=1, document_type_id=1,
        section_name=section_name, chunk_index=index, text=text,
    ), distance


def test_context_takes_limited_chunks_per_document_and_merges_neighbors_into_one_block():
    knowledge_base = KnowledgeBase(
        documents=[document("pravilnik", 0.1), document("uputstvo", 0.2)],
        chunks=[
            chunk("pravilnik", 0, "Član 1.", 0.10),
            chunk("pravilnik", 1, "Član 2.", 0.12),
            chunk("pravilnik", 5, "Član 6.", 0.15),
            chunk("uputstvo", 0, "Korak 1.", 0.30, section_name="Uvod"),
        ],
    )
    retrieval = RetrievalService(
        FixedEmbeddings(), knowledge_base, RetrievalConfig(max_chunks=3, max_chunks_per_document=2)
    )

    result = retrieval.retrieve_context(document_type_id=1, global_instruction="", section_instruction="")

    assert [(block.document_id, block.chunk_indices, block.text) for block in result.chunk_blocks] == [
        ("pravilnik", (0, 1), "[Opšte] Član 1. Član 2."),
        ("uputstvo", (0, 0), "[Uvod] Korak 1."),
    ]
