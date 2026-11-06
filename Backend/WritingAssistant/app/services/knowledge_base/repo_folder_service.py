from typing import Optional

from app.repository.knowledge_base.repo_folder_repository import RepoFolderRepository
from app.model.knowledge_base.repo_folder import RepoFolder
from app.schema.knowledge_base.repo_folder_schema import (
    RepoFolderOut, RepoFolderPageOut, RepoFolderQuery,
    CreateRepoFolder, PatchRepoFolder,
)
from app.schema.common.pagination_schema import PaginationMeta
from app.core.exceptions import NotFoundError


class RepoFolderService:
    def __init__(self, repo_folder_repository: RepoFolderRepository):
        self.repo_folder_repository = repo_folder_repository

    @staticmethod
    def _to_out(folder: RepoFolder) -> RepoFolderOut:
        return RepoFolderOut(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            created_by=folder.created_by,
            created_at=folder.created_at,
        )

    def list(self, page: int = 1, per_page: int = 20, parent_id: Optional[int] = None) -> RepoFolderPageOut:
        query = RepoFolderQuery(
            page=page,
            per_page=per_page,
            deleted=0,
            parent_id=parent_id,
            ordering="-created_at",
        )
        result = self.repo_folder_repository.read_page(query)

        return RepoFolderPageOut(
            items=[self._to_out(folder) for folder in result["items"]],
            meta=PaginationMeta(**result["pagination"]),
        )

    def get(self, folder_id: int) -> RepoFolderOut:
        return self._to_out(self.repo_folder_repository.read_by_id(folder_id))

    def add(self, create_schema: CreateRepoFolder, user_id: int) -> RepoFolderOut:
        if create_schema.parent_id is not None:
            self.repo_folder_repository.read_by_id(create_schema.parent_id)

        create_values = create_schema.copy(update={"created_by": user_id, "deleted": 0})
        return self._to_out(self.repo_folder_repository.create(create_values))

    def update(self, folder_id: int, patch_schema: PatchRepoFolder) -> RepoFolderOut:
        if patch_schema.parent_id is not None:
            try:
                self.repo_folder_repository.read_by_id(patch_schema.parent_id)
            except NotFoundError:
                raise NotFoundError(detail=f"Nadređeni folder {patch_schema.parent_id} ne postoji")

        return self._to_out(self.repo_folder_repository.update(folder_id, patch_schema))

    def remove(self, folder_id: int) -> None:
        self.repo_folder_repository.read_by_id(folder_id)

        folder_ids = self.repo_folder_repository.collect_descendant_ids(folder_id)
        self.repo_folder_repository.soft_delete_with_contents(folder_ids)
