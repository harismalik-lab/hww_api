"""
Validation for HotelWorldWide Hotel Details API.
"""
from flask_restful.inputs import regex

from common.constants.values import Companies, Currencies, Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import (boolean, currency,
                                                       language)

hww_hotel_details_api_parser = get_request_parser()

hww_hotel_details_api_parser.add_argument(
    'merchant_id',
    type=int,
    default=False,
    location=['mobile', 'json', 'values']
)
hww_hotel_details_api_parser.add_argument(
    'redeemability',
    type=regex('[a-zA-Z]*[_]*'),
    default='redeemable',
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'currency',
    type=currency,
    default=Currencies.AED,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'language',
    type=language,
    default=Locales.EN,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'offer_id',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'app_version',
    type=regex('[0-9][0-9]*[.]*'),
    required=False,
    default="0",
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    '__platform',
    type=regex('[a-zA-Z]'),
    required=False,
    default='',
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'device_key',
    type=regex('[a-zA-Z0-9]*[-]*[.]*'),
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'company',
    type=str,
    required=False,
    default=Companies.ENTERTAINER_FULL,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'outlet_id',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'param1',
    type=int,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'timezone',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'is_hww_instant_booking',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'query',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_details_api_parser.add_argument(
    'search_type',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
