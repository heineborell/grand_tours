from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Ride(BaseModel):
    activity_id: int
    distance: float = Field(..., ge=0, description="Ride in kilometers.")
    time: Optional[int] = Field(..., description="Time in hours:minutes.")
    elevation: Optional[int] = Field(..., description="Total ascension in meters.")
    avg_power: Optional[int] = Field(..., description="Average Power in watts.")
    tour_year: str = Field(..., description="Tour year and shows if its training or not")
    ride_date: date = Field(..., description="Date of the activity.")


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
                    "avg_power": ride.avg_power,
                    "time": ride.time,
                    "tour_year": ride.tour_year,
                    "ride_date": ride.ride_date,
                }
                for ride in self.rides
            ]
        )
