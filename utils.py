import os
import logging
import csv
import glob
import datetime
import json
import tempfile

from conf import *
from models.matching_trip import MatchingTrip


def create_working_dir():
    working_dir = os.path.join(
        tempfile.gettempdir(),
        "flights-matcher-" +
        (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y.%m.%d")
    )
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    return working_dir


def have_common_routes_been_retrieved(working_dir, first_origin_code, second_origin_code):
    logging.debug("have_origin_airports_been_processed: %s %s" % (first_origin_code, second_origin_code))

    filepath = os.path.join(
        working_dir,
        COMMON_AIRPORTS_FILENAME % (first_origin_code, second_origin_code)
    )

    return os.path.exists(filepath)


def calculate_matching_trips(first_origin_trips, second_origin_trips):
    matching_trips = list()

    for first_origin_trip in first_origin_trips:
        for second_origin_trip in second_origin_trips:
            if do_trips_dates_differ_at_most_one_day(first_origin_trip, second_origin_trip):
                matching_trips.append(MatchingTrip(first_origin_trip, second_origin_trip))

    return matching_trips


def do_trip_length_stay_in_range(go_flight, return_flight):
    return MIN_TRIP_LENGTH <= \
           get_days_difference(go_flight.departure_date(), return_flight.departure_date()) <= \
           MAX_TRIP_LENGTH


def do_trips_dates_differ_at_most_one_day(one_trip, two_trip):
    departure_days_difference = get_days_difference(
        one_trip.go_trip.departure_date(),
        two_trip.go_trip.departure_date()
    )

    return_days_difference = get_days_difference(
        one_trip.return_trip.departure_date(),
        two_trip.return_trip.departure_date()
    )

    if departure_days_difference == 0 and return_days_difference == 0:
        return True
    if departure_days_difference == 0 and return_days_difference == 1:
        return True
    if departure_days_difference == 0 and return_days_difference == -1:
        return True
    if departure_days_difference == 1 and return_days_difference == 0:
        return True
    if departure_days_difference == 1 and return_days_difference == -1:
        return True
    if departure_days_difference == -1 and return_days_difference == 0:
        return True
    if departure_days_difference == -1 and return_days_difference == 1:
        return True

    return False


def update_trips(trip_list, new_trip):

    for index, trip in enumerate(trip_list):
        # checking same departure and return date
        if new_trip.go_trip.departure_date() == trip.go_trip.departure_date() and \
                new_trip.return_trip.departure_date() == trip.return_trip.departure_date():

            # checking lower amount
            if new_trip.get_amount() < trip.get_amount():
                trip_list[index] = new_trip
                return

    trip_list.append(new_trip)


def read_from_csv_file(working_dir, clazz, filename):
    logging.debug("read_from_csv_file: %s %s %s" % (working_dir, clazz, filename))

    elements = list()

    with open(os.path.join(working_dir, filename), "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")

            element = clazz()
            element.put_data_from_array(line.split(","))

            elements.append(element)

    return elements


def clear_flights_files(working_dir, first_origin_code, second_origin_code):
    logging.debug("clear_flights_files: %s" % working_dir)

    flights_files = \
        glob.glob(
            os.path.join(
                working_dir,
                GO_FLIGHTS_FILENAME % (first_origin_code, second_origin_code)
            )
        ) + \
        glob.glob(
            os.path.join(
                working_dir,
                RETURN_FLIGHTS_FILENAME % (first_origin_code, second_origin_code)
            )
        ) + \
        glob.glob(
            os.path.join(
                working_dir,
                MATCHING_TRIPS_FILENAME % (first_origin_code, second_origin_code, "*")
            )
        )

    for flights_file in flights_files:
        logging.debug("clear_flights_files: %s" % flights_file)

        os.remove(flights_file)


def write_to_csv_file(working_dir, elements, filename):
    logging.debug("write_to_csv_file: %s %s" % (len(elements), filename))

    with open(os.path.join(working_dir, filename), "w") as f:
        writer = csv.writer(f)

        for element in elements:
            writer.writerow(element.get_data_as_array())


def is_new_airport(working_dir, origin_code, airport):
    logging.debug("is_new_airport: %s %s %s" % (working_dir, origin_code, airport.code))

    return not has_destination_airport_been_processed(working_dir, origin_code, airport.code) and \
           not (airport.code in CODE_BLACKLIST)


def has_destination_airport_been_processed(working_dir, origin_code, destination_code):
    logging.debug("has_destination_airport_been_processed: %s %s %s" % (working_dir, origin_code, destination_code))

    filepath = os.path.join(
        working_dir,
        GO_FLIGHTS_FILENAME % (origin_code, destination_code)
    )

    return os.path.exists(filepath)


def get_days_difference(departure_date, return_date):
    a = datetime.datetime.strptime(departure_date, '%Y-%m-%d')
    b = datetime.datetime.strptime(return_date, '%Y-%m-%d')

    return (b - a).days


def pretty_print_json_data(json_data):
    print(json.dumps(json_data, sort_keys=True, indent=2))


def trip_in_range(trip):
    if MIN_TRIP_LENGTH:
        if trip.days < MIN_TRIP_LENGTH:
            return False

    if MAX_TRIP_LENGTH:
        if trip.days > MAX_TRIP_LENGTH:
            return False

    return True
