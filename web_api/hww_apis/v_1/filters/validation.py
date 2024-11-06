"""
Validation for hww filters api
"""

from common.constants.values import Locales
from common.utils.api_utils import get_request_parser
from common.utils.custom_fields_request_parser import language

hww_filters_api_parser = get_request_parser()

hww_filters_api_parser.add_argument(
    'language',
    type=language,
    required=False,
    default=Locales.EN,
    location=['mobile', 'json', 'values']
)
