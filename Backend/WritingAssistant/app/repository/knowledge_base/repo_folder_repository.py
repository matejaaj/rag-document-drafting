from contextlib import AbstractContextManager
from typing import Callable, Iterable

from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.model.knowledge_base.repo_folder import RepoFolder
from app.model.knowledge_base.storage_object import StorageObject


class RepoFolderRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, RepoFolder)

    def list_child_folder_ids(self, session: Session, parent_ids: Iterable[int]) -> list[int]:
        if not parent_ids:
            return []
        rows = (
            session.query(RepoFolder.id)
            .filter(
                RepoFolder.deleted == 0,
                RepoFolder.parent_id.in_(list(parent_ids)),
            )
            .all()
        )
        return [row[0] for row in rows]

    def collect_descendant_ids(self, root_id: int) -> list[int]:
        with self.session_factory() as session:
            all_ids: list[int] = []
            current_level: list[int] = [root_id]
            while current_level:
                all_ids.extend(current_level)
                current_level = self.list_child_folder_ids(session, current_level)
            return all_ids

    def soft_delete_with_contents(self, folder_ids: list[int]) -> None:
        with self.session_factory() as session:
            self.soft_delete_storage_objects_in_folders(session, folder_ids)
            self.soft_delete_folders(session, folder_ids)
            session.commit()

    def soft_delete_folders(self, session: Session, folder_ids: list[int]) -> None:
        if not folder_ids:
            return
        (
            session.query(RepoFolder)
            .filter(RepoFolder.id.in_(folder_ids))
            .update({"deleted": 1}, synchronize_session=False)
        )

    def soft_delete_storage_objects_in_folders(self, session: Session, folder_ids: list[int]) -> None:
        if not folder_ids:
            return
        (
            session.query(StorageObject)
            .filter(
                StorageObject.repo_folder_id.in_(folder_ids),
                StorageObject.deleted == 0,
            )
            .update({"deleted": 1}, synchronize_session=False)
        )
