from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.model.chat.section_draft import SectionDraft

class SectionDraftRepository(BaseRepository):
    DEFAULT_ORDERING = "-id"

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, SectionDraft)
