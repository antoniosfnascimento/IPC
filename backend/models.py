from typing import List, Optional, Tuple

from pydantic import BaseModel


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
    city: Optional[str] = None


class SnapPointRequest(BaseModel):
    coords: Tuple[float, float]  # (lat, lng)
    city: Optional[str] = None
