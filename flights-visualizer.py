#!/usr/bin/env python3

import os
import glob
import datetime

from utils import create_working_dir
from conf import MATCHING_TRIPS_FILENAME

TOP_VALUES = 1000

FIRST_ORIGIN_CODE = ""
SECOND_ORIGIN_CODE = ""

MAX_FIRST_ROUND_TRIP_AMOUNT = 150
MAX_SECOND_ROUND_TRIP_AMOUNT = 100

FIRST_TRIP_LENGTHS = [0, 0]  # 3 nights, 2 free days
SECOND_TRIP_LENGTHS = [0, 0]  # 3 nights, 2 free days

FIRST_ORIGIN_DEPARTURE_WEEKDAYS = [0, 1, 2, 3, 4, 5, 6]  # 0 is monday
SECOND_ORIGIN_DEPARTURE_WEEKDAYS = [0, 1, 2, 3, 4, 5, 6]  # 0 is monday

AIRPORT_BLACKLIST = [
    "BGY",
    "TRN",
]


def get_matching_trips_filenames():
    if len(FIRST_ORIGIN_CODE) == 0:
        wildcard_1 = "*"
    else:
        wildcard_1 = FIRST_ORIGIN_CODE

    if len(SECOND_ORIGIN_CODE) == 0:
        wildcard_2 = "*"
    else:
        wildcard_2 = SECOND_ORIGIN_CODE

    wildcard = os.path.join(
        create_working_dir(),
        MATCHING_TRIPS_FILENAME % (wildcard_1, wildcard_2, "*")
    )

    return glob.glob(wildcard)


def get_top_lines(files):
    lines = list()

    for filename in files:
        with open(filename, "r") as f:
            file_lines = f.readlines()

            count = 0
            for line in file_lines:
                lines.append(line.replace("\n", ""))

                count += 1

                if count == TOP_VALUES:
                    break

    return lines


def is_trip_cost_acceptable(line, trip_number, max_amount):
    if trip_number == 0:
        trip_amount_index = 4
    else:
        trip_amount_index = 9

    return int(line.split(",")[trip_amount_index]) <= max_amount


def does_trip_departure_day_match_weekdays(line, trip_number, weekdays):
    if trip_number == 0:
        trip_departure_day_index = 2
    else:
        trip_departure_day_index = 7

    departure_date = line.split(",")[trip_departure_day_index]

    d = datetime.datetime.strptime(departure_date, '%Y-%m-%d')

    if d.weekday() in weekdays:
        return True

    return False


def does_trip_match_trip_lengths(line, trip_number, trip_lengths):
    if trip_lengths[0] == 0:
        return True

    if trip_number == 0:
        trip_departure_day_index = 2
        trip_return_day_index = 3
    else:
        trip_departure_day_index = 7
        trip_return_day_index = 8

    departure_date = line.split(",")[trip_departure_day_index]
    return_date = line.split(",")[trip_return_day_index]

    d = datetime.datetime.strptime(departure_date, '%Y-%m-%d')
    r = datetime.datetime.strptime(return_date, '%Y-%m-%d')

    length = (r - d).days
    # print(length)

    if trip_lengths[0] <= length <= trip_lengths[1]:
        # print("valid")
        return True

    # print("invalid")
    return False


filenames = get_matching_trips_filenames()

top_lines = get_top_lines(filenames)

# BDS	BLQ	2021-12-28	2022-01-03	72	CRL	BLQ	2021-12-27	2022-01-03	66	Bologna
# 0 	1 	2 			3 			4 	5 	6 	7 			8 			9	10

# filtering trips amount
top_lines = [line for line in top_lines
             if is_trip_cost_acceptable(line, 0, MAX_FIRST_ROUND_TRIP_AMOUNT) and
             is_trip_cost_acceptable(line, 1, MAX_SECOND_ROUND_TRIP_AMOUNT)]

# filtering departure day of week
top_lines = [line for line in top_lines
             if does_trip_departure_day_match_weekdays(line, 0, FIRST_ORIGIN_DEPARTURE_WEEKDAYS) and
             does_trip_departure_day_match_weekdays(line, 1, SECOND_ORIGIN_DEPARTURE_WEEKDAYS)]

# filtering trip length
top_lines = [line for line in top_lines
             if does_trip_match_trip_lengths(line, 0, FIRST_TRIP_LENGTHS) and
             does_trip_match_trip_lengths(line, 1, SECOND_TRIP_LENGTHS)]

# filtering blacklisted airports
top_lines = [line for line in top_lines if not (line.split(",")[1] in AIRPORT_BLACKLIST)]

# sort by first airport amount
# top_lines.sort(key=lambda line: int(line.split(",")[4]), reverse=True)

# sort by second airport amount
top_lines.sort(key=lambda line: int(line.split(",")[9]), reverse=True)

# print results
for line in top_lines:
    print(line)
