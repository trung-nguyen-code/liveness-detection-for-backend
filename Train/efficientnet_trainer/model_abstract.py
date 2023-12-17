from __future__ import annotations
from abc import abstractmethod


class AbstractClassifier:
    """
    Each distinct product of a product family should have a base interface. All
    variants of the product must implement this interface.
    """

    @abstractmethod
    def model_log(self):
        pass
