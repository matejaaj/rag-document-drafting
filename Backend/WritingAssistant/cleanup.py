from app.core.vector_client import get_client
from app.model.rag.vector_models import DOCUMENT_COLL, CHUNK_COLL

def drop_collections():
    client = get_client()
    for coll in [DOCUMENT_COLL, CHUNK_COLL]:
        if coll in client.collections.list_all():
            print(f"Dropping collection: {coll}")
            client.collections.delete(coll)
        else:
            print(f"Collection not found: {coll}")

if __name__ == "__main__":
    drop_collections()
