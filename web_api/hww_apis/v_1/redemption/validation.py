"""
Validation redemption Api
"""
from common.constants.values import Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import (boolean, currency,
                                                       language)

redemption_parser = get_request_parser()
redemption_parser.add_argument(
    'offer_id',
    required=True,
    action='append',
    location=['mobile', 'values', 'json'],
    help='offer_id required (array).'
)
redemption_parser.add_argument(
    'quantity',
    type=int,
    default=1,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'isshared',
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_shared',
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'outlet_id',
    type=int,
    required=True,
    location=['mobile', 'values', 'json'],
    help='outlet_id required (integer).'
)
redemption_parser.add_argument(
    'merchant_pin',
    type=int,
    required=True,
    location=['mobile', 'values', 'json'],
    help='merchant_pin required (integer).'
)
redemption_parser.add_argument(
    'currency',
    type=currency,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    '__lng',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    '__lat',
    type=float,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_reattempt',
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'transaction_id',
    type=str,
    required=True,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'product_id',
    type=str,
    required=True,
    location=['mobile', 'values', 'json'],
    help='product_id required (integer).'
)
redemption_parser.add_argument(
    'location_id',
    type=int,
    default=0,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'language',
    type=language,
    default=Locales.EN,
    required=False,
    location=['mobile', 'values', 'json'],
)
redemption_parser.add_argument(
    '__i',
    type=int,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    '__sid',
    type=int,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_delivery',
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'device_model',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    '__platform',
    type=str,
    required=True,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'triggered_by',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'app_version',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_family_offer',
    type=boolean,
    required=False,
    default=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_birthday_offer',
    type=boolean,
    required=False,
    default=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_family_offer[]',
    type=boolean,
    required=False,
    default=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_birthday_offer[]',
    type=boolean,
    required=False,
    default=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'company',
    type=str,
    required=False,
    default='entertainer',
    location=['mobile', 'values', 'json']
)
