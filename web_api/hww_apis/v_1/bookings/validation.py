"""
Validation for HotelWorldWide Bookings API.
"""

from common.constants.values import Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import language

hww_bookings_api_parser = get_request_parser()

hww_bookings_api_parser.add_argument(
    name="language",
    required=False,
    default=Locales.EN,
    type=language,
    location=['mobile', 'values', 'json']
)
