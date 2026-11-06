from app.model import PromptVersion
from tests.integration.seed import ADMIN, WRITER

PROMPT_VERSIONS_URL = "/writing-assistant/prompt-versions"


def test_writer_cannot_activate_a_prompt_version(client_for, seed):
    writer = client_for(WRITER)

    response = writer.post(f"{PROMPT_VERSIONS_URL}/{seed.inactive_report_version.id}/activate")

    assert response.status_code == 403


def test_activated_version_becomes_the_only_active_version_of_its_prompt(client_for, seed):
    admin = client_for(ADMIN)

    response = admin.post(f"{PROMPT_VERSIONS_URL}/{seed.inactive_report_version.id}/activate")

    assert response.status_code == 200
    versions = admin.get(PROMPT_VERSIONS_URL, params={"prompt_id": seed.report_prompt.id}).json()["items"]
    assert [version["id"] for version in versions if version["is_active"]] == [seed.inactive_report_version.id]


def test_active_prompt_version_cannot_be_deleted(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.delete(f"{PROMPT_VERSIONS_URL}/{seed.active_report_version.id}")

    assert response.status_code == 409
    with database.session() as session:
        assert session.get(PromptVersion, seed.active_report_version.id).deleted == 0


def test_inactive_prompt_version_is_deleted(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.delete(f"{PROMPT_VERSIONS_URL}/{seed.inactive_report_version.id}")

    assert response.status_code == 204
    with database.session() as session:
        assert session.get(PromptVersion, seed.inactive_report_version.id).deleted == 1


def test_two_versions_of_a_prompt_cannot_share_a_name(client_for, seed, database):
    admin = client_for(ADMIN)

    response = admin.post(
        PROMPT_VERSIONS_URL,
        json={"prompt_id": seed.report_prompt.id, "name": "v1", "prompt_text": "Nova verzija {CURRENT_SECTION_NAME}."},
    )

    assert response.status_code == 400
    with database.session() as session:
        assert session.query(PromptVersion).filter_by(prompt_id=seed.report_prompt.id, name="v1").count() == 1
