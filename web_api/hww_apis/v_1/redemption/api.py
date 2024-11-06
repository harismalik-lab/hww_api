import requests
from flask import current_app, request

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.constants.strings import CommonStrings
from common.utils.api_utils import (handle_response_in_case_of_error,
                                    process_request_response_data)
from common.utils.authentication import get_current_customer
from web_api.hww_apis.v_1.redemption.validation import redemption_parser


class HwwRedemption(BasePostResource):
    """
    Implementation: Validate the existence of the offers, the user, the outlet, and whether the offers are
    redeemable by this user at this outlet. From the outlet, merchant information can be retrieved
    and the PIN can then be verified. If all is OK, create a new record in the redemption table and
    calculate the redemption_code.
    """
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='redemption/redemption_api.log',
        ),
        'name': 'redemption_api'
    }
    logger = None
    request_parser = redemption_parser
    status_code = 422
    required_token = True
    strict_token = True

    def populate_request_arguments(self):
        self.company = self.request_args.get('company')

    def initialize_local_variables(self):
        """
        Initializes local variables.
        """
        self.customer = get_current_customer()
        self.user_id = self.customer.get('customer_id')
        self.session_token = self.customer.get('session_token')

    def handle_redemption_process(self):
        """
        Gets redemption data based on company, If company is entertainer then request is send to the B2C, else
        redemption request is send to B2B
        """
        try:
            request_data = {}
            request_data.update(self.request_args)
            request_data.update({
                'user_id': self.user_id,
                'session_token': self.session_token,
                'offer_id': int(request_data['offer_id'][0]),
                'wlcompany': self.company,
                '__i': self.user_id,
                '__sid': self.customer.get('id'),
                'analytics_company': self.company
            })
            self.response = requests.post(
                current_app.config.get('REDEMPTION_URL'),
                json=request_data,
                headers={"Authorization": request.environ.get('HTTP_AUTHORIZATION')}
            )
        except Exception as e:
            self.logger.exception(e)

    def generate_final_response(self):
        """
        Generates the final response in case of success.
        """
        if self.response.status_code in [200, 201]:
            self.redemption_response_data = process_request_response_data(self.response, company=self.company)
            if 'data' in self.redemption_response_data:
                self.redemption_response_data['data']["analytics_source_type"] = CommonStrings.ANALYTICS_SOURCE_TYPE_ENT
            self.send_response_flag = True
            self.status_code = 200
            return self.set_response(self.redemption_response_data, self.status_code)

        if self.response.status_code == 404:
            self.status_code = self.response.status_code
            self.send_response_flag = True
            self.status_code = 404
            self.response = {
                "message": self.response.text,
                "success": False,
                "data": {},
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)
        self.response, self.status_code = handle_response_in_case_of_error(self.response)
        self.send_response_flag = True
        return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Handles request for redemption request.
        """
        self.initialize_local_variables()
        self.handle_redemption_process()
        self.generate_final_response()
