"""
Validation for HotelWorldWide Booking Inquiry API.
"""
from common.constants.values import Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import language

hww_booking_inquiry_api_parser = get_request_parser()

hww_booking_inquiry_api_parser.add_argument(
    'language',
    type=language,
    required=False,
    default=Locales.EN,
    location=['mobile', 'json', 'values']
)

hww_booking_inquiry_api_parser.add_argument(
    'location_id',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json']
)
hww_booking_inquiry_api_parser.add_argument(
    'merchant_id',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json']
)
hww_booking_inquiry_api_parser.add_argument(
    'outlet_id',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json']
)
hww_booking_inquiry_api_parser.add_argument(
    'additional_details',
    type=str,
    required=False,
    default='',
    location=['mobile', 'values', 'json']
)
hww_booking_inquiry_api_parser.add_argument(
    'check_in_date',
    type=float,
    required=True,
    location=['mobile', 'values', 'json']
)
hww_booking_inquiry_api_parser.add_argument(
    'check_out_date',
    type=float,
    required=True,
    location=['mobile', 'values', 'json']
)
hww_booking_inquiry_api_parser.add_argument(
    'rooms',
    type=str,
    default='{}',
    required=False,
    help='Rooms JSON data',
    location=['mobile', 'json', 'values']
)
hww_booking_inquiry_api_parser.add_argument(
    'salutation',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
hww_booking_inquiry_api_parser.add_argument(
    'first_name',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
hww_booking_inquiry_api_parser.add_argument(
    'family_name',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
hww_booking_inquiry_api_parser.add_argument(
    'email',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
hww_booking_inquiry_api_parser.add_argument(
    'phone',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
