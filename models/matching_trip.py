
class MatchingTrip:
    def __init__(self, first_trip, second_trip):
        self.first_trip = first_trip
        self.second_trip = second_trip

    def __str__(self):
        return "%s\n%s" % (self.first_trip, self.second_trip)

    def get_data_as_array(self):
        return \
            self.first_trip.get_data_as_array() + \
            self.second_trip.get_data_as_array() + \
            [self.first_trip.go_trip.destination_name]
