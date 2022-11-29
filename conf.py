# DATES
DEPARTURE_DATE = "2022-12-15"
RETURN_DATE = "2022-12-22"

START_DATE = "2022-12-01"
END_DATE = "2023-01-08"

CURRENCIES = {  # euro to X
    "DKK": 7.44,  # corona danese
    "EUR": 1.0,  # euro
    "CZK": 24.40,  # corona ceca
    "GBP": 0.86,  # sterlina britannica
    "HUF": 413.17,  # fiorino ungherese
    "MAD": 11.12,  # dirhan marocchino
    "PLN": 4.70,  # zloty polacco
    "SEK": 10.83,  # corona svedese
}

# TRIPE LENGTHS
MIN_TRIP_LENGTH = 1  # 6 is for one week, e.g. from monday to next monday
MAX_TRIP_LENGTH = 7  # 6 is for one week, e.g. from monday to next monday

# AMOUNT
MAX_TRIP_AMOUNT = 200

# CODES
FIRST_ORIGIN_CODES = [
    "BDS",
    "BRI",
    #"TRN",
]
SECOND_ORIGIN_CODES = [
    "BRU",
    "CRL",
    "MST",
    "EIN",
]
CODE_BLACKLIST = [
    "BGY",
    #"BCN",
    "BDS",
    "BRI",
    "BUD",
    #"FCO",
    #"MAD",
    #"MLA",
    "MXP",
    #"PEG",
    "VIE",
]

# FILE NAMES
COMMON_AIRPORTS_FILENAME = "common_airports_for_%s-%s.csv"
GO_FLIGHTS_FILENAME = "go_%s-%s.csv"
RETURN_FLIGHTS_FILENAME = "return_%s-%s.csv"
MATCHING_TRIPS_FILENAME = "matching_%s_%s_%s.csv"

# WAIT INTERVALS
MIN_WAIT_INTERVAL = 10
MIN_WAIT_INTERVAL_RANGE = 10

# URLs
ROUTES_BASE_URL = "https://www.ryanair.com/api/locate/v1/autocomplete/routes?"\
                  "arrivalPhrase=&"\
                  "departurePhrase={}&"\
                  "market=it-it"
FLEX_DAYS = 3
FARES_BASE_URL = "https://www.ryanair.com/api/booking/v4/it-it/availability?" \
                 "ADT=1" \
                 "&CHD=0" \
                 "&DateIn=" \
                 "&DateOut={}" \
                 "&Destination={}" \
                 "&Disc=0" \
                 "&INF=0" \
                 "&Origin={}" \
                 "&TEEN=0" \
                 "&promoCode=" \
                 "&IncludeConnectingFlights={}" \
                 f"&FlexDaysBeforeOut={FLEX_DAYS}" \
                 f"&FlexDaysOut={FLEX_DAYS}" \
                 "&ToUs=AGREED"
