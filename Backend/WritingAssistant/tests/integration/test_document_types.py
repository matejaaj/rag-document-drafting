from app.model import DocumentType
from tests.integration.seed import ADMIN, WRITER

DOCUMENT_TYPES_URL = "/writing-assistant/document-types"


def test_default_document_type_cannot_be_renamed(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.patch(f"{DOCUMENT_TYPES_URL}/{seed.default_document_type.id}", json={"name": "Opšti"})

    assert response.status_code == 409
    with database.session() as session:
        assert session.get(DocumentType, seed.default_document_type.id).name == "Default"


def test_document_type_in_use_cannot_be_deleted(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.delete(f"{DOCUMENT_TYPES_URL}/{seed.report_document_type.id}")

    assert response.status_code == 409
    with database.session() as session:
        assert session.get(DocumentType, seed.report_document_type.id).deleted == 0


def test_unused_document_type_is_deleted(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.delete(f"{DOCUMENT_TYPES_URL}/{seed.unused_document_type.id}")

    assert response.status_code == 204
    with database.session() as session:
        assert session.get(DocumentType, seed.unused_document_type.id).deleted == 1


def test_writer_can_list_document_types(client_for, seed):
    writer = client_for(WRITER)

    response = writer.get(DOCUMENT_TYPES_URL)

    assert response.status_code == 200
    assert seed.report_document_type.name in [document_type["name"] for document_type in response.json()["items"]]


def test_creating_a_deleted_document_type_again_restores_it(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.post(DOCUMENT_TYPES_URL, json={"name": "Ponuda"})

    assert response.status_code == 200
    assert response.json()["id"] == seed.deleted_document_type.id
    with database.session() as session:
        assert session.query(DocumentType).filter_by(name="Ponuda").one().deleted == 0
