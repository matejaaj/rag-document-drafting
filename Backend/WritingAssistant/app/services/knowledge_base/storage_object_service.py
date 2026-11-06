from __future__ import annotations
from pathlib import Path
from typing import Optional

from app.repository.knowledge_base.storage_object_repository import StorageObjectRepository
from app.model.knowledge_base.storage_object import StorageObject
from app.schema.knowledge_base.storage_object_schema import (
    StorageObjectOut, StorageObjectPageOut, StorageObjectQuery, PatchStorageObject
)
from app.schema.common.pagination_schema import PaginationMeta
from app.core.exceptions import ValidationError

from app.services.rag.vector_ingestion_service import VectorIngestionService
from app.services.rag.vector_service import VectorService


DOCUMENT_STORAGE_DIR = Path("app/storage/objects")


class StorageObjectService:
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

    def __init__(
        self,
        storage_object_repository: StorageObjectRepository,
        vector_ingestion_service: VectorIngestionService,
        vector_service: VectorService,
    ):
        self.storage_object_repository = storage_object_repository
        self.vector_ingestion_service = vector_ingestion_service
        self.vector_service = vector_service

    @staticmethod
    def _to_out(storage_object: StorageObject) -> StorageObjectOut:
        return StorageObjectOut(
            id=storage_object.id,
            original_name=storage_object.original_name,
            mime_type=storage_object.mime_type,
            size_bytes=storage_object.size_bytes,
            repo_folder_id=storage_object.repo_folder_id,
            path=storage_object.path,
            created_by=storage_object.created_by,
            created_at=storage_object.created_at,
        )

    def store_file(
        self,
        *,
        content: bytes,
        original_name: str,
        mime_type: Optional[str],
        storage_dir: Path,
        created_by: Optional[int],
        repo_folder_id: Optional[int],
        session,
    ) -> int:
        storage_object = self.storage_object_repository.save_to_storage(
            content=content,
            original_name=original_name,
            mime_type=mime_type,
            storage_dir=storage_dir,
            created_by=created_by,
            repo_folder_id=repo_folder_id,
            session=session,
        )
        return storage_object.id

    def list(self, page: int = 1, per_page: int = 20, repo_folder_id: Optional[int] = None) -> StorageObjectPageOut:
        query = StorageObjectQuery(
            page=page,
            per_page=per_page,
            deleted=0,
            repo_folder_id=repo_folder_id,
            ordering="-created_at",
        )
        result = self.storage_object_repository.read_page(query)
        return StorageObjectPageOut(
            items=[self._to_out(storage_object) for storage_object in result["items"]],
            meta=PaginationMeta(**result["pagination"]),
        )

    def add_from_upload(
        self,
        *,
        filename: str,
        content: bytes,
        mime_type: Optional[str],
        repo_folder_id: Optional[int],
        created_by: int,
        document_type_id: int,
    ) -> StorageObjectOut:
        if not content:
            raise ValidationError(detail="Fajl je prazan")
        if len(content) > self.MAX_FILE_SIZE_BYTES:
            raise ValidationError(detail="Fajl je prevelik")
        if not filename:
            raise ValidationError(detail="Nedostaje naziv fajla")

        saved_file_path: Optional[str] = None
        try:
            # committed only after the document is in the vector store
            with self.storage_object_repository.transaction() as transaction:
                storage_object = self.storage_object_repository.save_to_storage(
                    content=content,
                    original_name=filename,
                    mime_type=mime_type,
                    storage_dir=DOCUMENT_STORAGE_DIR,
                    repo_folder_id=repo_folder_id,
                    created_by=created_by,
                    session=transaction,
                )
                saved_file_path = storage_object.path

                if self.vector_ingestion_service:
                    self.vector_ingestion_service.ingest_uploaded_document(
                        content=content,
                        filename=storage_object.original_name or "upload.bin",
                        mime_type=storage_object.mime_type,
                        storage_object_id=storage_object.id,
                        document_type_id=document_type_id,
                        title=storage_object.original_name,
                    )

                return self._to_out(storage_object)
        except Exception:
            if saved_file_path:
                self.storage_object_repository.remove_file(saved_file_path)
            raise

    def get(self, object_id: int) -> StorageObjectOut:
        return self._to_out(self.storage_object_repository.read_by_id(object_id))

    def update_metadata(self, object_id: int, patch_schema: PatchStorageObject) -> StorageObjectOut:
        return self._to_out(self.storage_object_repository.update(object_id, patch_schema))

    def remove(self, object_id: int) -> None:
        if self.vector_service:
            self.vector_service.delete_by_storage_object_id(object_id)

        self.storage_object_repository.delete_by_id(object_id)
