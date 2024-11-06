"""
Validation for HotelWorldWide Home API.
"""
from flask_restful.inputs import regex

from common.constants.strings import CommonStrings
from common.constants.values import Currencies, Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import (boolean, currency,
                                                       language)

hww_hotel_listing_api_parser = get_request_parser()

hww_hotel_listing_api_parser.add_argument(
    'platform',
    type=regex('[a-zA-Z]*'),
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'location_id',
    type=int,
    default=0,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'radius',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'is_map_search',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'json', 'values']
)
hww_hotel_listing_api_parser.add_argument(
    'language',
    type=language,
    default=Locales.EN,
    required=False,
    location=['mobile', 'values', 'json']
)

hww_hotel_listing_api_parser.add_argument(
    'app_version',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'sort',
    type=regex('[a-z_]*'),
    required=False,
    default='default',
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    '__lat',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    '__lng',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'd_lat',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'd_lng',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'map_lat',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'map_lng',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'category',
    type=str,
    required=False,
    default=CommonStrings.CATEGORY_TRAVEL,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'offset',
    type=int,
    default=0,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'limit',
    type=int,
    default=10,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'currency',
    type=currency,
    default=Currencies.USD,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'is_travel',
    type=boolean,
    default=True,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'show_instant_booking_hotels',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'search_type',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'query',
    type=str,
    required=False,
    default='',
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'offer_attributes[]',
    type=str,
    action='append',
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'offer_attributes',
    type=str,
    action='append',
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'merchant_attributes',
    type=str,
    action='append',
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'sub_categories',
    type=str,
    action='append',
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'sub_categories[]',
    type=str,
    action='append',
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'merchant_attributes[]',
    type=str,
    action='append',
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'billing_city',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'billing_country',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'is_recently_viewed_listing',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)
hww_hotel_listing_api_parser.add_argument(
    'screen_title',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)
