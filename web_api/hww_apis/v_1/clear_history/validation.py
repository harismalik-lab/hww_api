"""
Validation for Hww Clear History API.
"""
from flask_restful.inputs import regex

from common.utils.api_utils import get_request_parser

hww_clear_history_parser = get_request_parser()


hww_clear_history_parser.add_argument(
    'section_identifier',
    required=True,
    type=regex('[a-zA-Z]*'),
    location=['mobile', 'values', 'json']
)
