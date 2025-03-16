from typing import List, Optional

from pydantic import BaseModel, Field


class Ride(BaseModel):
    activity_id: int
    distance: float = Field(..., gt=0, description="Ride in kilometers.")
    time: float = Field(..., gt=0, description="Time in hours:minutes.")
    elevation: int = Field(..., gt=0, description="Total ascension in meters.")
    avg_power: Optional[int] = None


class Rider(BaseModel):
    strava_id: int = Field(..., gt=0, description="Rider strava unique id.")
    name: str = Field(..., description="Rider's name")
    rides: List[dict]
