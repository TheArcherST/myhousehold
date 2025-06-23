from collections.abc import Mapping
from datetime import datetime
from typing import Iterable, Any
from uuid import uuid4

from pymongo import MongoClient
from pymongo.synchronous.collection import Collection as MongoCollection

from .object import Object


sentinel_current_datetime: object = object()


class MongoCollectionsManager:
    def __init__(
            self,
            mongo_client: MongoClient,
    ):
        self._mongo_client = mongo_client
        self._mongo_main_database = mongo_client.get_database(
            f"myhousehold-main-{uuid4()}")
        self._mongo_derivatives_database = mongo_client.get_database(
            "myhousehold-derivatives")

    def get_claims_collection(self):
        return self._mongo_main_database.get_collection(
            "claims")

    def get_new_revision_collection(self, revision_at: datetime):
        return self._mongo_derivatives_database.get_collection(
            f"revision-{revision_at}")

    def get_new_transitions_collection(
            self,
            predicate: Object,
            period_start: datetime,
            period_end: datetime,
    ):
        return self._mongo_derivatives_database.get_collection(
            # todo: stable hash
            f"transitions"
            f"-{hash(frozenset(predicate))}"
            f"-{period_start}"
            f"-{period_end}"
        )


class UniversalSet:
    def __init__(self, mongo_collection: MongoCollection):
        self._mongo_collection = mongo_collection

    def add(self, o: Object) -> None:
        if self._mongo_collection.find_one(o) is None:
            self._mongo_collection.insert_one(o)

    def remove(self, o: Object) -> None:
        self._mongo_collection.delete_one(o)

    def _predicate_to_query_items(
            self,
            predicate: Object, *,
            prefix: str = "",
    ) -> Iterable[tuple[str, Any]]:
        for k, v in predicate.items():
            name = "{}.{}".format(prefix, k)
            if isinstance(v, Mapping):
                yield from self._predicate_to_query_items(
                    predicate=Object(v),
                    prefix=name,
                )
            yield name, v

    def find(self, predicate: Object) -> Iterable[Object]:
        expr = (self._mongo_collection
                .find(predicate))

        for i in expr:
            del i["_id"]
            yield Object(i)

    def find_one(self, where: Object) -> Object:
        result = list(self.find(where))
        if len(result) != 1:
            raise ValueError(result)
        return list(result)[0]

    @property
    def elements(self) -> frozenset[Object]:
        return frozenset(self.find(Object({})))
