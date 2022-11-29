import requests
import logging
import random
import datetime
import time
import math

from conf import *
from utils import clear_flights_files, write_to_csv_file, calculate_matching_trips, read_from_csv_file, do_trip_length_stay_in_range, update_trips, pretty_print_json_data

from models.airport import Airport
from models.flight import Flight
from models.trip import Trip


def retrieve_common_routes(working_dir, first_origin_code, second_origin_code):
    logging.debug("retrieve_common_routes: %s %s" % (first_origin_code, second_origin_code))

    clear_flights_files(working_dir, first_origin_code, second_origin_code)

    first_origin_routes = retrieve_routes(first_origin_code)
    second_origin_routes = retrieve_routes(second_origin_code)

    common_routes = list()

    for first_origin_route in first_origin_routes:
        for second_origin_route in second_origin_routes:
            if first_origin_route.code == second_origin_route.code:
                if not (any(first_origin_route.code == x.code for x in common_routes)):
                    common_routes.append(first_origin_route)

    return common_routes


def random_wait_before_request(reason, retries=0):
    s = random.randint(MIN_WAIT_INTERVAL + retries * MIN_WAIT_INTERVAL_RANGE,
                       MIN_WAIT_INTERVAL + MIN_WAIT_INTERVAL_RANGE + retries * MIN_WAIT_INTERVAL_RANGE)

    logging.info("sleeping for %s seconds for %s..." % (s, reason))

    time.sleep(s)


def retrieve_routes(origin_code):
    arrival_airports = list()

    exception_occurred = True
    retries = 0

    while exception_occurred:
        try:
            random_wait_before_request("routes from %s" % origin_code)

            resp = requests.get(ROUTES_BASE_URL.format(origin_code))
            data = resp.json()

            exception_occurred = False
        except Exception as ex:
            print(ex)

            exception_occurred = True
            retries += 1

    for element in data:
        code = element["arrivalAirport"]["code"]
        name = element["arrivalAirport"]["name"]

        is_direct = True
        connecting_airport = None

        if element["connectingAirport"]:
            pretty_print_json_data(element)
            is_direct = False

            connecting_airport_code = element["connectingAirport"]["code"]
            connecting_airport_name = element["connectingAirport"]["name"]
            connecting_airport = Airport(connecting_airport_code, connecting_airport_name, True)

        airport = Airport(code, name, is_direct, connecting_airport)
        arrival_airports.append(airport)

    return arrival_airports


def retrieve_trips_for_date(origin, destination, include_connecting_flights, date_out):
    logging.debug(f"retrieve_direct_availability_for_date: {origin} {destination} {include_connecting_flights} {date_out}")

    tmp_flights = list()

    exception_occurred = True
    retries = 0

    if include_connecting_flights:
        icf = "true"
    else:
        icf = "false"

    while exception_occurred:
        try:
            random_wait_before_request("availability %s -> %s" % (origin, destination), retries)

            resp = requests.get(FARES_BASE_URL.format(date_out, destination, origin, icf))
            data = resp.json()

            exception_occurred = False
        except Exception as ex:
            print(ex)

            exception_occurred = True
            retries += 1

    if "trips" in data:
        currency = data["currency"]
        conversion_rate = CURRENCIES[currency]

        for trip in data["trips"]:
            origin = trip["origin"]
            destination = trip["destination"]
            origin_name = trip["originName"]
            destination_name = trip["destinationName"]

            for date in trip["dates"]:
                # pretty_print_json_data(date)

                for flight in date["flights"]:
                    if "regularFare" in flight:
                        # pretty_print_json_data(flight["regularFare"])

                        flight_key = flight["flightKey"]

                        segments = flight["segments"]
                        departure_time = segments[0]["time"][0]

                        for fare in flight["regularFare"]["fares"]:
                            amount = fare["amount"] / conversion_rate

                        flight = Flight(
                            flight_key,
                            origin,
                            destination,
                            origin_name,
                            destination_name,
                            departure_time,
                            math.ceil(amount)
                        )

                        tmp_flights.append(flight)

    logging.debug(f"retrieve_direct_availability_for_date: {origin} -> {destination} {len(tmp_flights)} retrieved trips")

    return tmp_flights


def retrieve_trips_for_origin(working_dir, origin_code, destination_code, include_connecting_flights, online):
    logging.debug(f"retrieve_trips_for_origin: {working_dir} {origin_code} {destination_code} {include_connecting_flights} {online}")

    trips = list()

    if online:
        start_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
        cursor_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(END_DATE, "%Y-%m-%d")

        go_flights = list()
        return_flights = list()

        while cursor_date < end_date:
            logging.debug(f"retrieve_trips_for_origin: {cursor_date}")

            go_flights.extend(
                retrieve_trips_for_date(
                    origin_code,
                    destination_code,
                    include_connecting_flights,
                    cursor_date
                )
            )

            return_flights.extend(
                retrieve_trips_for_date(
                    destination_code,
                    origin_code,
                    include_connecting_flights,
                    cursor_date
                )
            )

            cursor_date = cursor_date + datetime.timedelta(days=7)

        write_to_csv_file(
            working_dir,
            go_flights,
            GO_FLIGHTS_FILENAME % (origin_code, destination_code)
        )

        write_to_csv_file(
            working_dir,
            return_flights,
            RETURN_FLIGHTS_FILENAME % (destination_code, origin_code)
        )
    else:
        go_flights = read_from_csv_file(
            working_dir,
            Flight,
            GO_FLIGHTS_FILENAME % (origin_code, destination_code)
        )

        return_flights = read_from_csv_file(
            working_dir,
            Flight,
            RETURN_FLIGHTS_FILENAME % (destination_code, origin_code)
        )

    for go_flight in go_flights:
        for return_flight in return_flights:
            if do_trip_length_stay_in_range(go_flight, return_flight):
                trip = Trip(go_flight, return_flight)
                if trip.get_amount() < MAX_TRIP_AMOUNT:
                    # trips.append(trip)
                    update_trips(trips, trip)

    return trips


def calculate_matching_trips_for_destination(working_dir, first_origin_code, second_origin_code, destination_code, include_connecting_flights=False, online=True):
    logging.debug(f"retrieve_availability_for_destination: {working_dir} {first_origin_code} {second_origin_code} {destination_code} {include_connecting_flights} {online}")

    first_origin_trips = retrieve_trips_for_origin(
        working_dir,
        first_origin_code,
        destination_code,
        include_connecting_flights,
        online
    )

    if len(first_origin_trips) == 0:
        logging.debug(f"retrieve_availability_for_destination: no trips for {first_origin_code}")
        return

    #for fot in first_origin_trips: print(fot)

    second_origin_trips = retrieve_trips_for_origin(
        working_dir,
        second_origin_code,
        destination_code,
        include_connecting_flights,
        online
    )

    if len(second_origin_trips) == 0:
        logging.debug(f"retrieve_availability_for_destination: no trips for {second_origin_code}")
        return

    #for sot in second_origin_trips: print(sot)

    matching_trips = calculate_matching_trips(first_origin_trips, second_origin_trips)

    #for mt in matching_trips: print(mt)

    if matching_trips:
        matching_trips.sort(
            key=lambda matching_trip: (
                matching_trip.second_trip.get_amount(),
                matching_trip.first_trip.get_amount(),
                matching_trip.first_trip.go_trip.departure_date(),
            ),
            reverse=False, # False is needed for flight-visualizer.py
        )

        write_to_csv_file(
            working_dir,
            matching_trips,
            MATCHING_TRIPS_FILENAME % (first_origin_code, second_origin_code, destination_code)
        )
