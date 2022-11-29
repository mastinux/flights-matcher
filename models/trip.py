import sys
sys.path.append('../')

from utils import get_days_difference


class Trip:
    def __init__(self, go_trip, return_trip):
        self.go_trip = go_trip
        self.return_trip = return_trip

    def __str__(self):
        return "%s-%s (%s %s) %s € [%s days]" % (
            self.go_trip.origin_code, self.go_trip.destination_code,
            self.go_trip.departure_date(), self.return_trip.departure_date(),
            self.get_amount(), self.get_days())

    def get_days(self):
        return get_days_difference(
            self.go_trip.departure_date(),
            self.return_trip.departure_date()
        )

    def get_amount(self):
        return self.go_trip.amount + self.return_trip.amount

    def get_data_as_array(self):
        return [
            self.go_trip.origin_code,
            self.go_trip.destination_code,
            self.go_trip.departure_date(),
            self.return_trip.departure_date(),
            str(self.get_amount()).zfill(3)
        ]

