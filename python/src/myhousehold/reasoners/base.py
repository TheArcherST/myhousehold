import abc

from pydantic.json_schema import JsonSchemaValue

from myhousehold.core.models import Proposition


class BaseReasoner(abc.ABC):
    """
    Implements reasoning about objects that are intended to be recorded.
    """

    # todo: implement somehow drawing conclusion from premises, rather
    #  than from one single premise.
    # todo: think about declaring premise type using pydantic model
    #  specified in typehint.

    @abc.abstractmethod
    def declare_premise_schema(self) -> JsonSchemaValue:
        """
        Declare such type of objects is supported.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def premises_selector(self):
        """ I have no time """

        raise NotImplementedError

    @abc.abstractmethod
    def inference(self, premise: Proposition) -> list[Proposition]:
        """
        Draw an inference on basis of provided premise.
        """

        raise NotImplementedError
