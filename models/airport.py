
class Airport:
    def __init__(self, c="", n="", is_direct=True, connecting_airport=None):
        self.code = c
        self.name = n
        self.is_direct = is_direct
        self.connecting_airport = connecting_airport

    def __str__(self):
        return "%s (%s)" % (self.code, self.name)

    def get_data_as_array(self):
        if self.connecting_airport:
            return [self.code, self.name, self.is_direct] + self.connecting_airport.get_data_as_array()
        else:
            return [self.code, self.name, self.is_direct]

    def put_data_from_array(self, array_values):
        self.code = array_values[0]
        self.name = array_values[1]
        self.is_direct = eval(array_values[2])

        if not self.is_direct:
            connecting_airport_name = array_values[3]
            connecting_airport_code = array_values[4]
            connecting_airport_is_direct = array_values[5]

            self.connecting_airport = Airport(
                connecting_airport_code,
                connecting_airport_name,
                connecting_airport_is_direct
            )
