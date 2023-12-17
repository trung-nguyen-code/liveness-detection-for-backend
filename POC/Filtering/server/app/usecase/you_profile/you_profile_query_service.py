from abc import ABC, abstractmethod
from typing import Union, List

from app.constants.user import CommonInput, LocationInput, FeatureInput


class YouProfileQueryService(ABC):
    """YouProfileQueryService defines a query service inteface related You profile entity."""  # noqa

    @abstractmethod
    def search_by_profile(
        self, inputs: List[Union[CommonInput, LocationInput, FeatureInput]]
    ):
        raise NotImplementedError
