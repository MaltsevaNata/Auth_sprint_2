"""
Утилиты для Elasticsearch.
"""

import json
from typing import Iterable
from urllib.parse import urljoin

import requests


def bulk_insert(url: str, index: str, records: list[dict]) -> None:
    """
    Bulk-insert данных в указанный индекс Elasticsearch.
    """
    query_str = "\n".join(prepare_bulk_query(index, records)) + "\n"
    response = requests.post(
        urljoin(url, "_bulk"),
        data=query_str,
        headers={"Content-Type": "application/x-ndjson"},
    )
    assert response.ok


def prepare_bulk_query(index, records) -> Iterable[str]:
    for record in records:
        operation = json.dumps({"index": {"_index": index, "_id": record["id"]}})
        data = json.dumps(record)
        yield f"{operation}\n{data}"
