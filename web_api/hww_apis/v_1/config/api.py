"""
HWW Config api
"""
from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.constants.values import URLs
from repositories.v_1.config_repo import ConfigRepo
from web_api.hww_apis.v_1.config.validation import hww_hotel_config_api_parser


class HwwConfig(BasePostResource):
    request_parser = hww_hotel_config_api_parser
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='configs/configs_api.log',
        ),
        'name': 'configs'
    }

    def populate_request_arguments(self):
        """
        Populates the request arguments.
        """
        self.currency = self.request_args.get('currency').upper()

    def initialize_repos(self):
        """
        Initializes the HWW config repo
        """
        self.config_repo = ConfigRepo()

    def process_data(self):
        """
        Process the data of configurations.
        """
        self.data = {
            "analytics_url": URLs.ANALYTICS_URL,
            "ui_config": self.config_repo.UI_CONFIG,
            "user_selected_currency": self.config_repo.get_user_selected_currency(self.currency)
        }

    def generate_final_response(self):
        """
        Generates the final response.
        """
        self.send_response_flag = True
        self.response = {
            'data': self.data,
            'success': True,
            'message': 'success'
        }
        self.status_code = 200
        return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Handles request Hww Config API.
        """
        self.populate_request_arguments()
        self.initialize_repos()
        self.process_data()
        self.generate_final_response()
