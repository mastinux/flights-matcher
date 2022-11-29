#!/usr/bin/env python3

from utils import *
from services import *

from models.airport import Airport

logging.basicConfig(level=logging.DEBUG)

working_dir = create_working_dir()

first_origin_count = 1

for first_origin_code in FIRST_ORIGIN_CODES:
    logging.info(f"processing first origin {first_origin_code} ({first_origin_count}/{len(FIRST_ORIGIN_CODES)})")

    second_origin_count = 1

    for second_origin_code in SECOND_ORIGIN_CODES:
        logging.info(f"processing second origin {second_origin_code} ({second_origin_count}/{len(SECOND_ORIGIN_CODES)})")
        logging.info("%s -> %s" % (first_origin_code, second_origin_code))

        if have_common_routes_been_retrieved(working_dir, first_origin_code, second_origin_code):
            common_airports = read_from_csv_file(
                working_dir,
                Airport,
                COMMON_AIRPORTS_FILENAME % (first_origin_code, second_origin_code))
        else:
            common_airports = retrieve_common_routes(working_dir, first_origin_code, second_origin_code)
            write_to_csv_file(
                working_dir,
                common_airports,
                COMMON_AIRPORTS_FILENAME % (first_origin_code, second_origin_code))

        common_airports = [common_airport for common_airport in common_airports
                           if is_new_airport(working_dir, first_origin_code, common_airport)]

        random.shuffle(common_airports)
        logging.debug([ca.code for ca in common_airports])

        common_airports_count = 1
        for common_airport in common_airports:
            logging.info("processing destination %s (%s/%s)..." % (common_airport.code, common_airports_count, len(common_airports)))

            calculate_matching_trips_for_destination(
                working_dir,
                first_origin_code,
                second_origin_code,
                common_airport.code,
                include_connecting_flights=(not common_airport.is_direct)
            )

            common_airports_count += 1

        second_origin_count = second_origin_count + 1

    first_origin_count = first_origin_count + 1
