from typing import List, Optional, Sequence

from app.services.rag.retrieval_models import RetrievalResult


class PromptComposer:

    def build_rag_context(self, retrieval_result: Optional[RetrievalResult]) -> str:
        if not retrieval_result or not retrieval_result.chunk_blocks:
            return ""
        chunk_texts: List[str] = [chunk_block.text for chunk_block in retrieval_result.chunk_blocks]
        return "\n\n".join(chunk_texts).strip()

    def compose(
        self,
        section,
        session_sections: Sequence,
        prompt_template: Optional[str],
        global_instruction: Optional[str],
        section_instruction: Optional[str],
        rag_context: Optional[str] = None,
    ) -> str:
        current_section_name = (section.name or "").strip()

        section_names = ", ".join(
            [session_section.name.strip() for session_section in session_sections if session_section.name]
        )

        prompt = (prompt_template or "")
        prompt = prompt.replace("{CURRENT_SECTION_NAME}", current_section_name)
        prompt = prompt.replace("{SECTION_NAMES}", section_names)
        prompt = prompt.replace("{GLOBAL_INSTRUCTION}", (global_instruction or "").strip())
        prompt = prompt.replace("{SECTION_INSTRUCTION}", (section_instruction or "").strip())
        prompt = prompt.replace("{RAG_CONTEXT}", (rag_context or "").strip())

        return prompt.strip()
