"""
Hww Bookings API.
"""

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.constants.icons import Icons
from common.utils.authentication import get_current_customer
from repositories.v_1.bookings_repo import BookingsRepo
from web_api.hww_apis.v_1.bookings.validation import hww_bookings_api_parser


class HwwBookings(BasePostResource):
    required_token = True
    strict_token = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='bookings/bookings_api.log',
        ),
        'name': 'bookings'
    }
    logger = None
    request_parser = hww_bookings_api_parser

    def populate_request_arguments(self):
        """
        Populates the request arguments.
        """
        self.locale = self.request_args.get('language')

    def initialize_local_variables(self):
        """
        Initializes local variables to be used in a single request.
        """
        self.customer = get_current_customer()
        self.query_results = []
        self.data = {"screen_title": self.bookings_repo.MY_BOOKINGS_SCREEN_TITLE}

    def initialize_repos(self):
        """
        Initializes repos to be used in a request.
        """
        self.bookings_repo = BookingsRepo()

    def add_empty_booking_section(self):
        """
        Adds the empty booking section that is to be shown if there are no bookings present for the customer.
        """
        self.data['booking_empty_section'] = {
            "section_identifier": "section_empty_view",
            "section_title": "",
            "section_list": [
                {
                    "title": self.bookings_repo.NO_BOOKINGS_TITLE,
                    "sub_title": self.bookings_repo.NO_BOOKINGS_SUBTITLE,
                    "image_url": Icons.NO_BOOKINGS
                }
            ]
        }

    def add_bookings_sections(self):
        """
        Adds the upcoming and previous or empty booking section in the bookings API response.
        """
        upcoming_section, previous_section = self.bookings_repo.get_user_previous_and_upcoming_bookings(
            customer_id=self.customer.get('customer_id'),
            locale=self.locale
        )
        if upcoming_section or previous_section:
            if upcoming_section:
                self.data['upcoming_section'] = upcoming_section

            if previous_section:
                self.data['previous_section'] = previous_section
        else:
            self.add_empty_booking_section()

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
        Handles request Hww Bookings API.
        """
        self.initialize_repos()
        self.initialize_local_variables()
        self.add_bookings_sections()
        self.generate_final_response()
