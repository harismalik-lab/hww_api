"""
Validation for Hww Config API.
"""

from common.constants.values import Currencies
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import currency

hww_hotel_config_api_parser = get_request_parser()
hww_hotel_config_api_parser.add_argument(
    'currency',
    type=currency,
    default=Currencies.USD,
    required=False,
    location=['mobile', 'values', 'json']
)
