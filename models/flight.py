
class Flight:
    def __init__(self, flight_key="", origin_code="", destination_code="", origin_name="", destination_name="", departure_time="", amount=0):
        self.flight_key = flight_key
        self.origin_code = origin_code
        self.destination_code = destination_code
        self.origin_name = origin_name
        self.destination_name = destination_name
        self.departure_time = departure_time
        self.amount = int(amount)

    def __str__(self):
        return "%s %s € %s - %s" \
               % (self.departure_date(), str(self.amount).zfill(2), self.origin_code, self.destination_code)

    def departure_date(self):
        return self.departure_time.split("T")[0]

    def get_data_as_array(self):
        return [self.flight_key, self.origin_code, self.destination_code, self.origin_name, self.destination_name, self.departure_time, self.amount]

    def put_data_from_array(self, array_values):
        self.flight_key = array_values[0]
        self.origin_code = array_values[1]
        self.destination_code = array_values[2]
        self.origin_name = array_values[3]
        self.destination_name = array_values[4]
        self.departure_time = array_values[5]
        self.amount = int(array_values[6])
