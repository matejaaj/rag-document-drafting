from app.model import Template, TemplateSection
from tests.integration.seed import ADMIN

TEMPLATES_URL = "/writing-assistant/templates"


def upload(client, seed, content: bytes):
    return client.post(
        TEMPLATES_URL,
        data={"name": "Projektni izveštaj", "document_type_id": seed.report_document_type.id},
        files={"file": ("izvestaj.md", content, "text/markdown")},
    )


def test_uploaded_markdown_template_gets_a_section_per_heading(client_for, seed, database):
    admin = client_for(ADMIN)

    response = upload(admin, seed, "# Uvod\nTekst.\n## Metode\n# Zaključak\n".encode())

    assert response.status_code == 201
    with database.session() as session:
        sections = (
            session.query(TemplateSection)
            .filter_by(template_id=response.json()["id"])
            .order_by(TemplateSection.position)
            .all()
        )
    assert [section.name for section in sections] == ["Uvod", "Metode", "Zaključak"]


def test_empty_template_file_is_rejected(client_for, seed, database):
    admin = client_for(ADMIN)

    response = upload(admin, seed, b"")

    assert response.status_code == 422
    with database.session() as session:
        assert session.query(Template).filter_by(name="Projektni izveštaj").count() == 0
