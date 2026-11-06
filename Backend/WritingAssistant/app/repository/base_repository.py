from contextlib import AbstractContextManager, contextmanager
from typing import Any, Callable, Iterator, Type, TypeVar, Sequence


from sqlalchemy.orm.attributes import InstrumentedAttribute

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import DuplicatedError, NotFoundError
from app.model.base import Base
from app.util.query_builder import dict_to_sqlalchemy_filter_options

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository:
    DEFAULT_PAGE: int = 1
    DEFAULT_PER_PAGE: int = 20
    DEFAULT_ORDERING: str = "-id"

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model: Type[ModelType]) -> None:
        self.session_factory = session_factory
        self.model = model

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        """Unit of work: pass the yielded session to repository calls; commits on exit."""
        with self.session_factory() as session:
            yield session
            session.commit()

    @staticmethod
    def _page(filtered_query, ordered_query, page: int, per_page: int, ordering: str) -> dict:
        return {
            "items": ordered_query.limit(per_page).offset((page - 1) * per_page).all(),
            "pagination": {
                "page": page,
                "per_page": per_page,
                "ordering": ordering,
                "total_count": filtered_query.count(),
            },
        }

    def read_page(
        self,
        query_schema,
        load_relationships: Sequence[InstrumentedAttribute] = (),
    ) -> dict:
        with self.session_factory() as session:
            query_values: dict = query_schema.model_dump(exclude_none=True)
            ordering: str = query_values.get("ordering", self.DEFAULT_ORDERING)
            order_by_clause = (
                getattr(self.model, ordering[1:]).desc()
                if ordering.startswith("-")
                else getattr(self.model, ordering).asc()
            )

            query = session.query(self.model)
            for relationship in load_relationships:
                query = query.options(joinedload(relationship))
            filtered_query = query.filter(dict_to_sqlalchemy_filter_options(self.model, query_values))

            return self._page(
                filtered_query,
                filtered_query.order_by(order_by_clause),
                query_values.get("page", self.DEFAULT_PAGE),
                query_values.get("per_page", self.DEFAULT_PER_PAGE),
                ordering,
            )

    def read_by_id(
        self,
        id: int,
        load_relationships: Sequence[InstrumentedAttribute] = (),
    ):
        with self.session_factory() as session:
            query = session.query(self.model)
            for relationship in load_relationships:
                query = query.options(joinedload(relationship))

            entity = query.filter(self.model.id == id, self.model.deleted == 0).first()
            if not entity:
                raise NotFoundError(detail=f"Zapis {id} ne postoji")
            return entity

    def create(self, create_schema):
        with self.session_factory() as session:
            entity = self.model(**create_schema.model_dump())
            try:
                session.add(entity)
                session.commit()
                session.refresh(entity)
            except IntegrityError as error:
                raise DuplicatedError(detail="Zapis već postoji ili se poziva na nepostojeći zapis") from error
            return entity

    def update(self, id: int, update_schema):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == id).update(
                update_schema.model_dump(exclude_none=True)
            )
            session.commit()
            return self.read_by_id(id)

    def update_column(self, id: int, column: str, value: Any):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == id).update({column: value})
            session.commit()
            return self.read_by_id(id)

    def delete_by_id(self, id: int):
        with self.session_factory() as session:
            entity = session.query(self.model).filter(self.model.id == id).first()
            if not entity:
                raise NotFoundError(detail=f"Zapis {id} ne postoji")

            entity.deleted = 1
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
