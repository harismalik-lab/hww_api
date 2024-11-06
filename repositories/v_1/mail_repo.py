"""
Mail Repo module contains all the mails specific implementation and helper methods.
"""
import json

import requests
from flask import current_app

from common.constants.values import Companies, Locales
from common.utils.api_utils import (get_current_date_time,
                                    process_request_response_data)
from models.ent_send_email import EntSendEmail


class MailRepo(object):

    BOOKING_ENQUIRY_MERCHANT = 921
    BOOKING_ENQUIRY_CUSTOMER = 106

    PRIORITY_HIGH = EntSendEmail.PRIORITY_HIGH
    PRIORITY_MEDIUM = EntSendEmail.PRIORITY_MEDIUM
    PRIORITY_LOW = EntSendEmail.PRIORITY_LOW

    @staticmethod
    def get_phone_users_email(auth_token, user_company):
        """
        Returns users' email who have signed up via phone.

        Customers that have signed up through phone will have a dummy email in customer profile so we have to hit
        specific APIs to get their actual email.

        :param str auth_token: session token of customer.
        :param str user_company: company of the user.
        :return: user email.
        :rtype: str
        """
        user_email = ''

        if user_company == Companies.ALFUTAIM:
            user_api_url = current_app.config.get('AF_USER_INFO_URL')
            bearer_token = current_app.config.get('AF_BEARER_TOKEN')
            if user_api_url and bearer_token:
                request_data = {
                    "ext_auth_token": auth_token,
                }
                request_headers = {
                    'Authorization': 'Bearer {authentication_token}'.format(authentication_token=bearer_token)
                }
                response = requests.post(
                    user_api_url,
                    json=request_data,
                    headers=request_headers
                )
                if response.status_code == 200:
                    response_data = process_request_response_data(
                        response,
                        company=Companies.ALFUTAIM
                    )
                    if response_data:
                        user_email = response_data.get('data', {}).get('user_info', {}).get('email')

        return user_email

    @classmethod
    def send_email(cls, **kwargs):
        """
        Sends a specific email with data present in the respective keys of keyword arguments.

        This is achieved by making an entry in the EntSendEmail table of Consolidation schema which is then read by
        a scheduled script that sends email.

        Required params are:
        > email
        > email_type_id
        """

        dump = kwargs.get('dump')
        email_data = kwargs.get('email_data')
        optional_data = kwargs.get('optional_data')
        email_data = {
            'email_to': kwargs.get('email'),
            'email_template_type_id': kwargs.get('email_type_id'),
            'email_template_data': json.dumps(email_data) if dump else email_data,
            'optional_data': json.dumps(optional_data) if dump else optional_data,
            'language': kwargs.get('language', Locales.EN),
            'priority': kwargs.get('priority', cls.PRIORITY_LOW),
            'created_date': get_current_date_time()
        }
        return EntSendEmail.send_email(email_data)
