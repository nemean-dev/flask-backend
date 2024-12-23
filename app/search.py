from flask import current_app
from typing import List, Tuple

# any model that needs indexing needs to define a __searchable__ class 
# attribute that lists the fields that need to be included in the index

def add_to_index(index: str, model: object) -> None:
    """
    Args:
    - model is an object with an id and a __searchable__: list[str] attribute 
    with fields to index
    """
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)

def remove_from_index(index: str, model: object) -> None:
    """
    Args:
    - model is an object with an id and a __searchable__: list[str] attribute 
    with fields to index
    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index: str, query: str, page: int, per_page: int) -> Tuple[List[int], int]:
    """
    returns a tuple with:
    - a list of ids ordered by match score
    - the total number of results
    """
    if not current_app.elasticsearch:
        print('es not configured')
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']