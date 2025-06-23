import abc
import urllib
import urllib.parse

from pymongo import MongoClient
from src.myhousehold.mental_set import MentalSet
from src.myhousehold.universal_set import (
    MongoCollectionsManager,
    UniversalSet,
)
from src.myhousehold.object import Object


class BaseInstituteClient:
    """Base class for defining institute clients

    Institutes here are structures that defines basic abstractions from
    your life using basic theory under the hood.  All operations are
    performed within single, universal set.  Institutes defines objects
    that are introduced to universal set and implements base operations,
    related with that objects.

    Institute clients stays for entity that allows the end user of
    the institute to act within the institute.  Application doesn't
    try to fully model an institutes operation, but to model the
    interface between institute and a person, that will allow to pack
    all person actions into the operations, performed on institutional
    level.

    Institutes may require other institutes in order to function.

    The layer of abstraction of the institute definition must tend to
    Pareto-optimal for tasks of particular user.  Since there is no such
    user as the average member of end users, I think, abstraction
    flexibility must be preserved somehow.

    """

    def __init__(
            self,
            mental_set: MentalSet,
    ):
        self.__mental_set = mental_set

    # ===> abstract methods

    @abc.abstractmethod
    def init_axioms(self) -> None:
        pass

    @abc.abstractmethod
    def get_existence_predicates(self) -> list[Object]:
        pass

    # <===

    # ===> sandbox

    def _claim_exists(self, o: Object):
        return self.__mental_set.claim_exists(
            o,
            claim_predicates=self.get_existence_predicates(),
        )

    # <===


class InstituteClientIdentity(BaseInstituteClient):
    """Institute identity

    Defines basic model of personal identity and differentiated objects
    outside of this identity.

    """

    def get_existence_predicates(self) -> list[Object]:
        return [self.p_institute]

    def init_axioms(self):
        self._claim_exists(self.p_institute)
        self._claim_exists(self.p_person)
        self._claim_exists(self.p_me)
        self._claim_exists(self.p_society_member)

    # p_ fields defines predicates, that define abstractions for objects
    #  used in the mindset's institutional structure.  maybe it's
    #  convenient to treat p_ as `pointer`, but do not forget that it
    #  points not to one object but to set of objects

    @property
    def p_institute(self):
        # yes, institute materially exists as well as all other objects.
        #  it's like ask, did apple exists?  we'll exactly find an apple
        #  in the whole world, but apple is the same abstraction as
        #  institutional structures.
        # note: question did apples exists seems me equivalent to did
        #  apple exists question.
        return Object({
            "type": "identity_institute",
        })

    @property
    def p_person(self) -> Object:
        # properties, that tells us that object is a person
        return Object({
            "type": "person",
        })

    @property
    def p_me(self) -> Object:
        return Object(
            self.p_person
            | {"identity_type": "me"}
        )

    @property
    def p_society_member(self) -> Object:
        # just to be implicit.  this model assumes that app persons
        #  known to user included in his understanding of society
        return self.p_person


class InstituteClientSocialContracts(BaseInstituteClient):
    def get_existence_predicates(self) -> list[Object]:
        return [self.p_institute]

    def init_axioms(self) -> None:
        self._claim_exists(self.p_institute)

    @property
    def p_institute(self) -> Object:
        return Object({
            "type": "social_contracts_institute",
        })

    def claim_contract(
            self,
            label: str,
            participants: list[Object],
    ) -> None:
        """
        Claim that subjects are related between themselves
        with some liabilities.

        :param label:
        :param participants:
        :return:
        """

        self._claim_exists(Object({
            "type": "contract",
            "label": label,
            "participants": participants,
        }))


class InstituteClientOwnership(BaseInstituteClient):
    def __init__(
            self,
            mental_set: MentalSet,
            i_identity: InstituteClientIdentity,
            i_social_contracts: InstituteClientSocialContracts,
    ):
        super().__init__(mental_set)
        self._i_identity = i_identity
        self._i_social_contracts = i_social_contracts

    def get_existence_predicates(self) -> list[Object]:
        return [self._i_social_contracts.p_institute,
                self._i_identity.p_institute,
                self.p_institute]

    def init_axioms(self) -> None:
        self._claim_exists(self.p_institute)

    @property
    def p_institute(self):
        return Object({
            "type": "institute_ownership",
        })

    def claim_ownership(
            self, /,
            _object: Object, *,
            label: str,
    ):
        self._i_social_contracts.claim_contract(
            label=f"ownership:{label}",
            participants=[
                Object({
                    "subject": self._i_identity.p_society_member,
                    "liability": "protect_liability"
                }),
                Object({
                    "subject": self._i_identity.p_society_member,
                    "liability": "protect_ownership"
                }),
            ],
        )


def main():
    username = urllib.parse.quote_plus("root")
    password = urllib.parse.quote_plus("changeme")
    mongo_client = MongoClient(
        "mongodb://%s:%s@127.0.0.1:46161" % (username, password),
    )
    collections_manager = MongoCollectionsManager(mongo_client)
    mental_set = MentalSet(
        objects=UniversalSet(
            mongo_collection=collections_manager.get_claims_collection(),
        ),
        mongo_collections_manager=collections_manager,
    )
    i_identity = InstituteClientIdentity(
        mental_set,
    )
    i_identity.init_axioms()

    i_social_contracts = InstituteClientSocialContracts(
        mental_set,
    )
    i_social_contracts.init_axioms()

    i_ownership = InstituteClientOwnership(
        mental_set,
        i_identity,
        i_social_contracts,
    )
    i_ownership.init_axioms()

    i_ownership.claim_ownership(
        Object({
            "type": "fridge",
        }),
        label="my fridge",
    )
    i_ownership.claim_ownership(
        Object({
            "type": "fridge",
        }),
        label="my fridge",
    )
    objects = mental_set.get_universe_revision()
    ownership = objects.find_one(Object({"type": "ownership"}))
    print(ownership)
    print(ownership["object"]["name"])


if __name__ == '__main__':
    main()
