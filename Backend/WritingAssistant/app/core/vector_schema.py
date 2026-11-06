from __future__ import annotations
from typing import get_type_hints, get_origin, get_args, Union
from datetime import datetime
import types

from weaviate.classes.config import Property, DataType, Configure, VectorDistances
from app.core.vector_client import get_client
from app.model.rag.vector_models import DOCUMENT_COLL, CHUNK_COLL, DocumentVector, ChunkVector

def _vector_config():
    return Configure.Vectors.self_provided(
        vector_index_config=Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE,
            ef_construction=128,
            max_connections=64,
        )
    )

def _unwrap_optional(annotation):
    origin = get_origin(annotation)
    if origin in (Union, types.UnionType):
        type_arguments = [argument for argument in get_args(annotation) if argument is not type(None)]
        if len(type_arguments) == 1:
            return type_arguments[0]
    return annotation

def _python_type_to_weaviate_data_type(annotation) -> DataType:
    annotation = _unwrap_optional(annotation)
    origin = get_origin(annotation)
    type_arguments = get_args(annotation)

    if origin in (list, tuple):
        item_type = type_arguments[0] if type_arguments else str
        item_type = _unwrap_optional(item_type)
        if item_type is str:
            return DataType.TEXT_ARRAY
        if item_type is int:
            return DataType.INT_ARRAY
        if item_type is float:
            return DataType.NUMBER_ARRAY
        return DataType.TEXT_ARRAY

    if annotation is str:
        return DataType.TEXT
    if annotation is int:
        return DataType.INT
    if annotation is float:
        return DataType.NUMBER
    if annotation is datetime:
        return DataType.DATE
    return DataType.TEXT

def _model_properties(model_class) -> list[Property]:
    properties: list[Property] = []
    field_annotations = get_type_hints(model_class, include_extras=True)
    for field_name, annotation in field_annotations.items():
        if field_name == "id":
            continue
        data_type = _python_type_to_weaviate_data_type(annotation)
        properties.append(Property(name=field_name, data_type=data_type))
    return properties

def _ensure_collection(collection_name: str, model_class) -> None:
    weaviate_client = get_client()
    existing_collection_names = set(weaviate_client.collections.list_all())

    if collection_name not in existing_collection_names:
        weaviate_client.collections.create(
            name=collection_name,
            properties=_model_properties(model_class),
            vector_config=_vector_config(),
        )
    else:
        collection = weaviate_client.collections.get(collection_name)
        existing_properties = {existing_property.name: existing_property for existing_property in collection.config.get().properties}
        for model_property in _model_properties(model_class):
            if model_property.name not in existing_properties:
                collection.config.add_property(model_property)

def ensure_minimal_collections() -> None:
    _ensure_collection(DOCUMENT_COLL, DocumentVector)
    _ensure_collection(CHUNK_COLL, ChunkVector)
