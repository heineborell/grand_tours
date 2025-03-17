from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Ride(BaseModel):
    activity_id: int
    distance: float = Field(..., gt=0, description="Ride in kilometers.")
    time: Optional[int] = Field(..., description="Time in hours:minutes.")
    elevation: Optional[int] = Field(..., description="Total ascension in meters.")
    avg_power: Optional[int] = None
    tour_year: str = Field(..., description="Tour year and shows training or not")
    ride_date: date = Field(..., description="Date of the activity.")


class Rider(BaseModel):
    strava_id: int = Field(..., gt=0, description="Rider strava unique id.")
    name: str = Field(..., description="Rider's name")
    rides: List[Ride]
