from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session
from app.model.chat.section_instruction import SectionInstruction
from app.repository.base_repository import BaseRepository


class SectionInstructionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, SectionInstruction)
