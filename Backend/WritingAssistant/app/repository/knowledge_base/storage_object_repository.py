from __future__ import annotations
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Callable, Optional
import uuid

from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.model.knowledge_base.storage_object import StorageObject


class StorageObjectRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, StorageObject)

    def remove_file(self, path: str) -> None:
        Path(path).unlink(missing_ok=True)

    def save_to_storage(
        self,
        *,
        content: bytes,
        original_name: str,
        mime_type: Optional[str],
        storage_dir: Path,
        created_by: Optional[int] = None,
        repo_folder_id: Optional[int] = None,
        session: Optional[Session] = None,
    ) -> StorageObject:
        storage_dir.mkdir(parents=True, exist_ok=True)
        unique_file_name = f"{uuid.uuid4().hex}_{original_name}"
        file_path = storage_dir / unique_file_name
        file_path.write_bytes(content)

        def add_row(target_session: Session) -> StorageObject:
            storage_object = StorageObject(
                path=str(file_path),
                original_name=original_name,
                mime_type=mime_type,
                size_bytes=len(content),
                created_by=created_by,
                repo_folder_id=repo_folder_id,
            )
            target_session.add(storage_object)
            target_session.flush()
            return storage_object

        if session is not None:
            return add_row(session)

        with self.session_factory() as own_session:
            storage_object = add_row(own_session)
            own_session.commit()
            own_session.refresh(storage_object)
            return storage_object
