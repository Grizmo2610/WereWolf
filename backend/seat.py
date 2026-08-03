from dataclasses import dataclass


@dataclass
class Seat:
    seat_id: int
    angle_deg: float

    @staticmethod
    def build_circle(total_seats: int) -> list["Seat"]:
        step = 360 / total_seats
        return [Seat(seat_id=i, angle_deg=round(i * step, 2)) for i in range(total_seats)]
