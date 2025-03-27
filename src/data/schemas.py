from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Segment(BaseModel):
    name: str
    dist: Optional[float] = None
    time: Optional[int] = None
    vert: Optional[int] = None
    grade: Optional[float] = None


class Ride(BaseModel):
    activity_id: int
    distance: float = Field(..., ge=0, description="Ride in kilometers.")
    time: Optional[int] = Field(..., description="Time in hours:minutes.")
    elevation: Optional[int] = Field(..., description="Total ascension in meters.")
    avg_power: Optional[int] = Field(..., description="Average Power in watts.")
    tour_year: str = Field(..., description="Tour year and shows if its training or not")
    stage: Optional[str] = Field(None, description="Race stage.")
    ride_date: date = Field(..., description="Date of the activity.")
    race_start_day: date = Field(..., description="First day of the race that is considered.")
    segments: List[Segment]


class Rider(BaseModel):
    strava_id: int = Field(..., gt=0, description="Rider strava unique id.")
    name: str = Field(..., description="Rider's name")
    rides: List[Ride]

    def to_dataframe(self):
        import pandas as pd

        return pd.DataFrame(
            [
                {
                    "strava_id": self.strava_id,
                    "activity_id": ride.activity_id,
                    "distance": ride.distance,
                    "elevation": ride.elevation,
                    "avg_power": ride.avg_power,
                    "time": ride.time,
                    "tour_year": ride.tour_year,
                    "stage": ride.stage,
                    "ride_day": ride.ride_date,
                    "race_start_day": ride.race_start_day,
                    "segments": ride.segments,
                }
                for ride in self.rides
            ]
        )
