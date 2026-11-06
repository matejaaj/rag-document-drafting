from app.model import SectionDraft
from tests.integration.seed import WRITER

SECTIONS_URL = "/writing-assistant/session-sections"


def test_saved_draft_replaces_generated_text_and_later_saves_update_it(client_for, seed, database):
    writer = client_for(WRITER)
    section_id = seed.introduction_section.id
    writer.post(f"{SECTIONS_URL}/{section_id}/iterations", json={})

    writer.put(f"{SECTIONS_URL}/{section_id}/iterations/1/draft", json={"content": "Prva izmena."})
    response = writer.put(f"{SECTIONS_URL}/{section_id}/iterations/1/draft", json={"content": "Druga izmena."})

    assert response.status_code == 200
    assert response.json()["section_draft"]["content"] == "Druga izmena."
    with database.session() as session:
        assert session.query(SectionDraft).count() == 1
