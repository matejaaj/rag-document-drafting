from contextlib import AbstractContextManager
from typing import Callable, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.model.chat.chat_session import ChatSession
from app.repository.base_repository import BaseRepository

class ChatSessionRepository(BaseRepository):
    DEFAULT_ORDERING = "-updated_at"
    DEFAULT_PER_PAGE = 20

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, ChatSession)

    def search_by_term(self, user_id: int, term: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        pattern = f"%{term.upper()}%"

        with self.session_factory() as session:
            filtered_query = (
                session.query(ChatSession)
                .filter(
                    ChatSession.deleted == 0,
                    ChatSession.created_by == user_id,
                )
            ).filter(func.upper(ChatSession.title).like(pattern))

            ordered_query = filtered_query.order_by(ChatSession.updated_at.desc())

            return self._page(filtered_query, ordered_query, page, per_page, "-updated_at")
