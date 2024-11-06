"""
HWW Clear History API.
"""
from requests import codes

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.utils.authentication import get_current_customer
from models.mongo_models.searches import Searches
from models.mongo_models.viewed_hotels import ViewedHotels
from web_api.hww_apis.v_1.clear_history.validation import \
    hww_clear_history_parser


class HwwClearHistory(BasePostResource):
    request_parser = hww_clear_history_parser
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='clear_history/clear_history_api.log',
        ),
        'name': 'clear_history'
    }

    SEARCH_IDENTIFIER = 'section_recent_searches'
    HOME_IDENTIFIER = 'section_recent_hotels'

    def populate_request_arguments(self):
        """
        Set the class arguments using request_parser.
        """
        self.section_identifier = self.request_args.get('section_identifier')

    def initialize_local_variables(self):
        """
        Initializes local variables.
        """
        self.customer = get_current_customer()
        self.message = ''

    def process_data(self):
        """
        Process the data of Clear History API.

        >> Deactivates all searches made by the user stored in MONGO db if a user is logged in.
        """
        if self.customer['is_user_logged_in']:
            if self.section_identifier == self.SEARCH_IDENTIFIER:
                if Searches.deactivate_recent_searches(self.customer['customer_id']):
                    self.status_code = codes.ok
                else:
                    self.status_code = codes.already_reported
                self.success = True

            elif self.section_identifier == self.HOME_IDENTIFIER:
                if ViewedHotels.deactivate_viewed_hotels(customer_id=self.customer['customer_id']):
                    self.status_code = codes.ok
                else:
                    self.status_code = codes.already_reported
                self.success = True

            else:
                self.status_code = codes.not_implemented
                self.success = False
                self.message = 'Your suggested identifier {} is not valid. Please check again.'.format(
                    self.section_identifier
                )

        else:
            self.status_code = codes.unauthorized
            self.success = False
            self.message = 'User not logged in.'

    def generate_final_response(self):
        """
        Generates the final response.
        """
        self.send_response_flag = True
        self.response = {
            'success': self.success,
            'message': self.message,
            'code': self.status_code
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Handles request Hww Clear History API.
        """
        self.populate_request_arguments()
        self.initialize_local_variables()
        self.process_data()
        self.generate_final_response()
