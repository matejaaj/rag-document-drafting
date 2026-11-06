from app.model import OutputFeedback
from tests.integration.seed import OTHER_WRITER, WRITER


def test_writer_can_rate_only_text_from_own_document(client_for, seed, database):
    generation = client_for(WRITER).post(
        f"/writing-assistant/session-sections/{seed.introduction_section.id}/iterations", json={}
    )
    other_writer = client_for(OTHER_WRITER)

    response = other_writer.post(
        "/writing-assistant/output-feedback",
        json={"model_output_id": generation.json()["model_output"]["id"], "rating_value": 1},
    )

    assert response.status_code == 403
    with database.session() as session:
        assert session.query(OutputFeedback).count() == 0
