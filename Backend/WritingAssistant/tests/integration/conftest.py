import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.core.database import Database
from app.core.security import CurrentUser
from app.main import app, container
from app.model import Base
from tests.integration.seed import Seed


class FixedLLMClient:
    provider = "test-provider"
    model = "test-model"

    def generate_text(self, final_prompt):
        return "Generisan tekst.", {"usage": {"input_tokens": 1000, "output_tokens": 500}}


class EmptyVectorStore:
    def query_documents_by_vector(self, **kwargs):
        return []

    def query_chunks_by_vector(self, **kwargs):
        return []


class FixedEmbeddings:
    def embed_query(self, text):
        return [0.0]


@pytest.fixture(scope="session")
def database(tmp_path_factory):
    database = Database(f"sqlite:///{tmp_path_factory.mktemp('database') / 'writing_assistant.db'}")
    database.create_tables()
    container.database.override(providers.Object(database))
    # out-of-process systems: OpenAI, HuggingFace, Weaviate
    container.llm_client.override(providers.Object(FixedLLMClient()))
    container.embedding_service.override(providers.Object(FixedEmbeddings()))
    container.vector_repository.override(providers.Object(EmptyVectorStore()))
    yield database
    container.reset_override()


@pytest.fixture(autouse=True)
def seed(database):
    seed = Seed()
    with database.session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        for row in seed.all:  # parents first
            session.add(row)
            session.flush()
        session.commit()
        for row in seed.all:
            session.refresh(row)
    return seed


@pytest.fixture(autouse=True)
def working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # uploaded files are stored relative to it


@pytest.fixture
def client_for():
    def create_client(user: CurrentUser) -> TestClient:
        return TestClient(app, headers={"X-USER-ID": str(user.id), "X-USER-ROLE": user.role, "X-EMAIL": user.email})

    return create_client
