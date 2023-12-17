import time
from typing import List
import geopy.distance
import math
from app.constants.user import LocationInput


async def calculate_distance(
    user_location: LocationInput, candidates_location: List[LocationInput]
) -> List[float]:
    """
    Calculate the distance between the user and candidate
    """
    start_time = time.time()
    distances = []

    for location in candidates_location:
        distance = geopy.distance.distance(
            (
                user_location["latitude"],
                user_location["longitude"],
            ),
            (
                location["latitude"],
                location["longitude"],
            ),
        ).km
        distances.append(distance)
    end_time = time.time()
    print("Time to calculate distance: ", end_time - start_time)

    return distances
