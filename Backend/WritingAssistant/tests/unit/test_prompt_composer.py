from app.model import SessionSection
from app.services.chat.prompt_composer import PromptComposer
from app.services.rag.retrieval_models import ChunkBlock, RetrievalResult


def knowledge_chunk(text):
    return ChunkBlock(document_id="pravilnik", section_name=None, chunk_indices=(0, 0), text=text, distance=0.1)


def test_prompt_contains_section_names_instructions_and_knowledge_base_context():
    composer = PromptComposer()
    introduction = SessionSection(name="Uvod")
    sections = [introduction, SessionSection(name="Zaključak")]
    retrieval_result = RetrievalResult(
        doc_hits=[], chunk_blocks=[knowledge_chunk("Prvi deo pravilnika."), knowledge_chunk("Drugi deo pravilnika.")]
    )

    prompt = composer.compose(
        section=introduction,
        session_sections=sections,
        prompt_template=(
            "Sekcija {CURRENT_SECTION_NAME} od {SECTION_NAMES}.\n"
            "Dokument: {GLOBAL_INSTRUCTION}\nSekcija: {SECTION_INSTRUCTION}\nZnanje:\n{RAG_CONTEXT}"
        ),
        global_instruction=" Formalan ton. ",
        section_instruction="Dva pasusa.",
        rag_context=composer.build_rag_context(retrieval_result),
    )

    assert prompt == (
        "Sekcija Uvod od Uvod, Zaključak.\n"
        "Dokument: Formalan ton.\nSekcija: Dva pasusa.\nZnanje:\nPrvi deo pravilnika.\n\nDrugi deo pravilnika."
    )
