from __future__ import annotations
from app.services.llm.llm_service import LLMService

_SUMMARY_PROMPT = """Sažmi sledeći dokument na srpskom u 100–150 reči.
- Uklopi ključne brojke, datume, nazive sekcija i ciljeve.
- Bez uvodnog small talka, samo čist sažetak. U jednom paragrafu opisi sve, nemoj da stavljas brojeve, bullete, cist prepircan sadrzaj dokumenta.

DOKUMENT:
<<<
{document_text}
>>>"""

class SummarizationService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def summarize(self, text: str) -> str:
        prompt = _SUMMARY_PROMPT.format(document_text=text[:100_000])
        llm_result = self.llm_service.generate(prompt)
        if llm_result.status != "ok":
            raise RuntimeError(llm_result.error_message or "Summarization failed")
        return llm_result.generated_text.strip()
