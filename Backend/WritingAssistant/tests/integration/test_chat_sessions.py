from app.model import SessionSection
from tests.integration.seed import WRITER

CHAT_SESSIONS_URL = "/writing-assistant/chat-sessions"


def test_document_created_from_template_gets_its_sections_in_order(client_for, seed, database):
    writer = client_for(WRITER)

    response = writer.post(CHAT_SESSIONS_URL, json={"template_id": seed.report_template.id})

    assert response.status_code == 200
    with database.session() as session:
        sections = (
            session.query(SessionSection)
            .filter_by(session_id=response.json()["id"])
            .order_by(SessionSection.position)
            .all()
        )
    assert [section.name for section in sections] == ["Uvod", "Rezultati", "Zaključak"]


def test_writer_sees_only_own_documents(client_for, seed):
    writer = client_for(WRITER)

    response = writer.get(CHAT_SESSIONS_URL)

    assert response.status_code == 200
    assert {chat_session["id"] for chat_session in response.json()["items"]} == {
        seed.writer_report_session.id,
        seed.writer_minutes_session.id,
    }
