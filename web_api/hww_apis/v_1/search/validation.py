"""
Validation for HotelWorldWide Home API.
"""

from common.constants.values import Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import language

hww_search_api_parser = get_request_parser()


hww_search_api_parser.add_argument(
    name="language",
    required=False,
    default=Locales.EN,
    type=language,
    location=['mobile', 'values', 'json']
)

hww_search_api_parser.add_argument(
    'query',
    type=str,
    required=False,
    default='',
    location=['mobile', 'values', 'json']
)
hww_search_api_parser.add_argument(
    '__lat',
    type=float,
    required=False,
    default=0.0,
    location=['mobile', 'values', 'json']
)
hww_search_api_parser.add_argument(
    '__lng',
    type=float,
    required=False,
    default=0.0,
    location=['mobile', 'values', 'json']
)
