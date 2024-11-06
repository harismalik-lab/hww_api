"""
Hww Search API.
"""

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.constants.icons import Icons
from common.utils.authentication import get_current_customer
from repositories.v_1.search_repo import SearchRepo
from web_api.hww_apis.v_1.search.validation import hww_search_api_parser


class HwwSearch(BasePostResource):
    required_token = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='search/search_api.log',
        ),
        'name': 'search'
    }
    logger = None
    request_parser = hww_search_api_parser

    def populate_request_arguments(self):
        """
        Populates the request arguments.
        """

        self.locale = self.request_args.get('language')
        self.latitude = self.request_args.get('__lat')
        self.longitude = self.request_args.get('__lng')
        self.query = self.request_args.get('query')

    def initialize_local_variables(self):
        """
        Initializes local variables to be used in a single request.
        """

        self.customer = get_current_customer()
        self.query_results = []
        self.data = {"sections": []}

    def initialize_repos(self):
        """
        Initializes repos to be used in a request.
        """

        self.search_repo = SearchRepo()

    def add_autocomplete_results_section(self):
        """
        Adds auto-complete results in Search API call.

        :return: True if results found against query, else False.
        :rtype: bool
        """

        query_results = self.search_repo.get_auto_complete_results(
            query=self.query,
            lat=self.latitude,
            lng=self.longitude,
        )
        self.data["search_result"] = query_results
        if query_results:
            return True
        return False

    def add_empty_view_section(self):
        """
        Adds empty view section in Search if no results were found against query.
        """

        self.data['sections'].append({
            "section_identifier": "section_empty_view",
            "section_title": self.search_repo.EMPTY_SECTION_TITLE,
            "section_list": [{
                "title": self.search_repo.SEARCH_NO_RESULTS.format(query=self.query),
                "image_url": Icons.SEARCH_NO_RESULTS
            }]
        })

    def add_popular_destinations_section(self):
        """
        Adds popular destinations section in Search API call.
        """

        self.data["sections"].append(
            {
                "section_identifier": "section_popular_destination",
                "section_title": self.search_repo.SECTION_POPULAR_DESTINATIONS_TITLE,
                "section_subtitle": self.search_repo.SECTION_POPULAR_DESTINATIONS_TITLE,
                "url": "",
                "section_list": self.search_repo.get_popular_destinations(self.locale)
            }
        )

    def add_recent_searches_section(self):
        """
        Adds recent searches section in Search API call.
        :rtype: bool
        """

        if self.customer['is_user_logged_in']:
            recent_searches = self.search_repo.get_user_recent_searches(self.customer.get('customer_id'))
            if recent_searches:
                self.data['sections'].append({
                    "section_identifier": "section_recent_searches",
                    "section_title": self.search_repo.SECTION_RECENT_SEARCHES_TITLE,
                    "section_subtitle": self.search_repo.SECTION_RECENT_SEARCHES_TITLE,
                    "url": "",
                    "section_list": recent_searches,
                })
                return True
        return False

    def generate_final_response(self):
        """
        Generates the final response.
        """

        self.send_response_flag = True
        self.status_code = 200
        self.response = {
            "message": '',
            "success": True,
            "data": self.data,
            "code": self.status_code
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Handles request Hww Search API.
        """

        self.initialize_local_variables()
        self.initialize_repos()

        if self.query:
            if not self.add_autocomplete_results_section():
                self.add_empty_view_section()

        if not self.add_recent_searches_section():
            self.add_popular_destinations_section()

        self.generate_final_response()
