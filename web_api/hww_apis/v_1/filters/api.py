"""
Hww Filters API
"""

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from repositories.v_1.filters_repo import FiltersRepo
from web_api.hww_apis.v_1.filters.validation import hww_filters_api_parser


class HwwFilters(BasePostResource):
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='hww_filters/hww_filters_api.log',
        ),
        'name': 'hww_filters'
    }
    logger = None
    request_parser = hww_filters_api_parser
    required_token = True
    strict_token = False

    def populate_request_arguments(self):
        """
        Populates the request argument.
        """
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        """
        Initializes repos to be used in a request.
        """
        self.filters_repo = FiltersRepo()

    def get_filters_section(self):
        """
        Get filters section of hww filters
        """
        self.data = {
            "filter_sections": [
                self.filters_repo.FILTER_SECTION_INSTANT_BOOK,
                self.filters_repo.FILTER_SECTION_TRAVEL_STYLE,
                self.filters_repo.FILTER_SECTION_HOTEL_TYPES,
                self.filters_repo.get_filter_section_amenities(self.locale)
            ]
        }

    def generate_final_response(self):
        """
        Generates the final response.
        """
        self.send_response_flag = True
        self.status_code = 200
        self.response = {
            "message": 'success',
            "success": True,
            "data": self.data,
            "code": self.status_code
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Handles request for hotel world wide filters.
        """
        self.initialize_repos()
        self.get_filters_section()
        self.generate_final_response()
