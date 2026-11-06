from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.model import PromptExecution, SectionIteration
from tests.integration.seed import ADMIN, OTHER_WRITER, WRITER


def generation_url(section):
    return f"/writing-assistant/session-sections/{section.id}/iterations"


def test_each_generation_of_a_section_is_saved_as_its_next_iteration(client_for, seed, database):
    writer = client_for(WRITER)

    first = writer.post(generation_url(seed.introduction_section), json={"section_instruction": "Kratko."})
    second = writer.post(generation_url(seed.introduction_section), json={"section_instruction": "Duže."})

    assert [first.status_code, second.status_code] == [200, 200]
    assert [first.json()["seq_no"], second.json()["seq_no"]] == [1, 2]
    with database.session() as session:
        stored_seq_nos = [
            iteration.seq_no
            for iteration in session.query(SectionIteration).filter_by(session_section_id=seed.introduction_section.id)
        ]
    assert sorted(stored_seq_nos) == [1, 2]


def test_generation_uses_active_prompt_version_of_session_document_type(client_for, seed, database):
    writer = client_for(WRITER)

    response = writer.post(generation_url(seed.introduction_section), json={})

    assert response.status_code == 200
    with database.session() as session:
        execution = session.query(PromptExecution).one()
    assert execution.prompt_version_id == seed.active_report_version.id


def test_generation_falls_back_to_default_prompt_when_document_type_has_none(client_for, seed, database):
    writer = client_for(WRITER)

    response = writer.post(generation_url(seed.agenda_section), json={})

    assert response.status_code == 200
    with database.session() as session:
        execution = session.query(PromptExecution).one()
    assert execution.prompt_version_id == seed.active_default_version.id


def test_test_session_generates_with_its_pinned_version_instead_of_the_active_one(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.post(generation_url(seed.test_session_section), json={})

    assert response.status_code == 200
    with database.session() as session:
        execution = session.query(PromptExecution).one()
    assert execution.prompt_version_id == seed.inactive_report_version.id


def test_generation_records_cost_by_active_model_pricing(client_for, seed, database):
    writer = client_for(WRITER)

    writer.post(generation_url(seed.introduction_section), json={})

    with database.session() as session:
        execution = session.query(PromptExecution).one()
    # 1000 input tokens at $2 and 500 output tokens at $8 per million
    assert execution.cost_usd == Decimal("0.006")
    assert execution.pricing_id == seed.test_model_pricing.id


def test_writer_cannot_generate_text_in_another_writers_session(client_for, seed, database):
    other_writer = client_for(OTHER_WRITER)

    response = other_writer.post(generation_url(seed.introduction_section), json={})

    assert response.status_code == 403
    with database.session() as session:
        assert session.query(PromptExecution).count() == 0


def test_request_without_signed_in_user_is_rejected(seed):
    anonymous = TestClient(app)

    response = anonymous.post(generation_url(seed.introduction_section), json={})

    assert response.status_code == 401
