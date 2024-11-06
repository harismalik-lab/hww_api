"""
Validation for HotelWorldWide Home API.
"""
from common.constants.values import Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import currency, language

hww_home_api_parser = get_request_parser()

hww_home_api_parser.add_argument(
    'language',
    type=language,
    required=False,
    default=Locales.EN,
    location=['mobile', 'json', 'values']
)

hww_home_api_parser.add_argument(
    'location_id',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json']
)
hww_home_api_parser.add_argument(
    'currency',
    type=currency,
    required=False,
    default="PKR",
    location=['mobile', 'values', 'json']
)
