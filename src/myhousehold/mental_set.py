from datetime import datetime

from .universal_set import (
    UniversalSet,
    MongoCollectionsManager,
)
from .object import Object


sentinel_current_datetime: object = object()
sentinel_empty_list: object = object()


class MentalSet:
    """
    Describes the world as it can be represented in the user's mind,
    using self-contained abstractions grounded in pure set theory.
    Methods here directly represent operations, that I use when I trying
    to thought strictly.

    Few words about abstractions.  Is we declare that fridges are
    coolers, actually, we declare that all objects that can be
    identified as fridges must also be identified as coolers too;
    all generic properties of coolers are properties of fridges
    too.  You define all references between object in a very agile
    way when using the mental set: you just describe abstraction
    that restricts object to be sufficient for your purpose.
    Application may introduce tools to verify, that chosen abstraction
    is really good for your situation, but you do not forced to
    reference objects using identifiers, such do most applications,
    because it's really convenient for application itself, but
    involve additional cognitive load for user, at my glance.

    """

    def __init__(
            self,
            objects: UniversalSet,
            mongo_collections_manager: MongoCollectionsManager,
    ):
        self._objects = objects
        self._mongo_collections_manager = mongo_collections_manager

    def claim_exists(
            self, /,
            _object: Object, *,
            # note: circular existence predicates now allowed, and will
            #  introduce evaluation symmetry problems.  It must be
            #  resolved.  I think we must resolve such existence
            #  dependencies in favor of the existence of favor objects.
            claim_predicates: list[Object] = sentinel_empty_list,
            made_at: datetime = sentinel_current_datetime,
    ) -> None:
        """ Claim that you thought about some object """

        if claim_predicates is sentinel_empty_list:
            claim_predicates = list()
        if made_at is sentinel_current_datetime:
            made_at = datetime.now()

        self._objects.add(Object({
            "type": "claim_exists",
            "object": _object,
            "claim_predicates": claim_predicates,
            "made_at": made_at,
        }))
    
    def claim_conforms(
            self,
            _object: Object,
            properties: Object,
    ):
        """ Claim that A objects have B properties in addition """

        return Object({
            "type": "claim_conforms",
            "object": _object,
            "properties": properties,
        })

    def claim_not_conforms(
            self,
            _object: Object,
            properties: Object,
    ):
        """ Claim that A objects does not have B properties """

        return Object({
            "type": "claim_not_conforms",
            "object": _object,
            "properties": properties,
        })

    def claim_doest_not_exists(
            self, /,
            _object: Object, *,
            claim_predicates: list[Object] = sentinel_empty_list,
            made_at: datetime = sentinel_current_datetime,
    ) -> None:
        """ Claim that you don't want to thought about the object """
        if claim_predicates is sentinel_empty_list:
            claim_predicates = list()
        if made_at is sentinel_current_datetime:
            made_at = datetime.now()

        self._objects.add(Object({
            "type": "claim_does_not_exists",
            "object": _object,
            "claim_predicates": claim_predicates,
            "made_at": made_at,
        }))

    def _claim_transition(
            self, /,
            old_object: Object,
            new_object: Object,
            claim_predicates: list[Object] = sentinel_empty_list,
            made_at: datetime = sentinel_current_datetime,
    ) -> None:
        # todo: up-to-date method
        """
        Claim that specified abstraction is changed.  For example, you
        had fridge that works, but it's broken.  So it's makes sense,
        that your working fridge now does not exists.  But Z
        """
        if claim_predicates is sentinel_empty_list:
            claim_predicates = list()
        if made_at is sentinel_current_datetime:
            made_at = datetime.now()

        self._objects.add(Object({
            "type": "claim_transition",
            "old_object": old_object,
            "new_object": new_object,
            "claim_predicates": claim_predicates,
            "made_at": made_at,
        }))

    def _change_claim(
            self, /,
            old_object: Object,
            _object: Object, *,
            existence_predicates: list[Object],
            made_at: datetime = sentinel_current_datetime,
    ) -> None:
        pass

    def get_object_claims(
            self, /,
            predicate: Object, *,
            period_start: datetime = datetime.min,
            period_end: datetime = sentinel_current_datetime
    ) -> UniversalSet:
        # todo: up-to-date method
        if period_end is sentinel_current_datetime:
            period_end = datetime.now()

        collection = (
            self._mongo_collections_manager
                .get_new_transitions_collection(
                predicate=predicate,
                period_start=period_start,
                period_end=period_end,
            ))
        result = UniversalSet(
            mongo_collection=collection,
        )

        claims = self._objects.find(Object({
            "$or": [{"type": "claim_exists"},
                    {"type": "claim_does_not_exists"}],
            "made_at": {"$gte": period_start, "$lt": period_end},
            **dict(zip(
                map(lambda x: "object." + x, predicate.keys()),
                predicate.values(),
            )),
        }))
        for i in sorted(claims, key=lambda x: x["made_at"]):
            result.add(i)

        return result

    def get_universe_revision(
            self,
            at: datetime = sentinel_current_datetime,
    ) -> UniversalSet:
        # todo: up-to-date method
        """
        Get UniversalSet of real objects, existing at timestamp, as
        implicated from claims
        """

        if at is sentinel_current_datetime:
            at = datetime.now()

        collection = self._mongo_collections_manager\
            .get_new_revision_collection(at)
        result = UniversalSet(
            mongo_collection=collection,
        )

        claims = self._objects.find(Object({
            "$or": [{"type": "claim_exists"},
                    {"type": "claim_does_not_exists"}],
            "made_at": {"$lte": at},
        }))

        for i in sorted(claims, key=lambda x: x["made_at"]):
            if i["type"] == "claim_exists":
                result.add(i["object"])
            elif i["type"] == "claim_does_not_exists":
                result.remove(i["object"])
            else:
                raise TypeError(i["type"])

        return result
