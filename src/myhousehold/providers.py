import urllib.parse
from typing import Iterable

from dishka import Provider, Scope, provide
from pymongo import MongoClient

from myhousehold.universal_set import MongoCollectionsManager, UniversalSet
from myhousehold.mental_set import MentalSet


class ProviderMongoDB(Provider):
    @provide(scope=Scope.APP)
    def get_mongo_client(self) -> Iterable[MongoClient]:
        username = urllib.parse.quote_plus("root")
        password = urllib.parse.quote_plus("changeme")
        mongo_client = MongoClient(
            "mongodb://%s:%s@127.0.0.1:46161" % (username, password),
        )
        with mongo_client as client:
            yield client

    @provide(scope=Scope.APP)
    def get_mongo_collections_manager(
            self,
            mongo_client: MongoClient,
    ) -> MongoCollectionsManager:
        return MongoCollectionsManager(
            mongo_client=mongo_client,
        )


class ProviderMentalSet(Provider):
    @provide(scope=Scope.APP)
    def get_mental_set(
            self,
            mongo_collections_manager: MongoCollectionsManager,
    ) -> MentalSet:
        collection = mongo_collections_manager.get_claims_collection()
        universal_set = UniversalSet(collection)
        return MentalSet(
            objects=universal_set,
            mongo_collections_manager=mongo_collections_manager,
        )
