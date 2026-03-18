from pydantic import BaseModel
from typing import List, Tuple

class UserProfile(BaseModel):
    profile_name: str
    max_incline: float
    min_width: float
    avoid_stairs: bool
    surface_preference: List[str]

class RouteRequest(BaseModel):
    start_coords: Tuple[float, float]
    end_coords: Tuple[float, float]
    profile: UserProfile
