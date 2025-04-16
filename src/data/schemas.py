from datetime import date
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field


class Segment(BaseModel):
    name: str
    dist: Optional[float] = None
    time: Optional[int] = None
    vert: Optional[int] = None
    grade: Optional[float] = None
    watt: Optional[int] = None
    heart_rate: Optional[int] = None


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

    def to_segment_df(self):
        rows = []
        for activity in self.rides:
            for segment in activity.segments:
                rows.append(
                    {
                        "activity_id": int(activity.activity_id),
                        "strava_id": int(self.strava_id),
                        "rider_name": self.name,
                        "tour_year": activity.tour_year,
                        "stage": activity.stage,
                        "total_distance": activity.distance,
                        "total_elevation": activity.elevation,
                        "ride_day": activity.ride_date,
                        "race_start_day": activity.race_start_day,
                        "segment_name": segment.name,
                        "distance": segment.dist,
                        "time": segment.time,
                        "vertical": int(segment.vert),
                        "grade": segment.grade,
                        "watt": segment.watt,
                        "heart_rate": segment.heart_rate,
                    }
                )
        df = pd.DataFrame(rows)
        return df if not df.empty else None
