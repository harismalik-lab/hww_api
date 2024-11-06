"""
Hww Booking Inquiry API.
"""
import collections
import json

from phpserialize import dumps as php_json_dumps
from requests import codes

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.utils.api_utils import (convert_timestamp_to_date,
                                    get_messages_locale)
from common.utils.authentication import get_current_customer
from models.booking_request import BookingRequest
from models.outlet import Outlet
from repositories.v_1.bookings_repo import BookingsRepo
from repositories.v_1.mail_repo import MailRepo
from web_api.hww_apis.v_1.booking_inquiry.validation import \
    hww_booking_inquiry_api_parser


class HwwBookingInquiry(BasePostResource):
    required_token = True
    strict_token = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='booking_inquiry/booking_inquiry_api.log',
        ),
        'name': 'booking_inquiry'
    }
    logger = None
    request_parser = hww_booking_inquiry_api_parser

    def populate_request_arguments(self):
        """
        Populates the request arguments.
        """
        self.location_id = self.request_args.get('location_id')
        self.merchant_id = self.request_args.get('merchant_id')
        self.outlet_id = self.request_args.get('outlet_id')
        self.locale = self.request_args.get('language')

        self.check_in_date = self.request_args.get('check_in_date')
        self.check_out_date = self.request_args.get('check_out_date')
        self.rooms_params = json.loads(self.request_args.get('rooms', {}))
        self.additional_details = self.request_args.get('additional_details')
        self.customer_salutation = self.request_args.get('salutation')
        self.customer_first_name = self.request_args.get('first_name')
        self.customer_family_name = self.request_args.get('family_name')
        self.customer_email = self.request_args.get('email')
        self.customer_phone = self.request_args.get('phone')

    def initialize_repos(self):
        """
        Initializes the different repos.
        """
        self.mail_repo = MailRepo()
        self.bookings_repo = BookingsRepo()

    def initialize_local_variables(self):
        """
        Initializes local variables.
        """
        self.customer = get_current_customer()
        self.messages_locale = get_messages_locale(self.locale)
        self.check_in_date = convert_timestamp_to_date(self.check_in_date)
        self.check_out_date = convert_timestamp_to_date(self.check_out_date)
        self.enquiry_number = None
        self.success_message = ''
        self.enquiry_id = 0
        self.customer_first_name = self.customer_first_name or self.customer.get('first_name')
        self.customer_family_name = self.customer_family_name or self.customer.get('family_name')
        self.customer_email = self.customer_email or self.customer.get('email')
        self.customer_phone = self.customer_phone or self.customer.get('mobile')

    def validate_booking_request(self):
        """
        Validates if the booking request is valid.

        This function checks the following things:

        The booking dates in case a booking has been done in the past.
        The rooms in case the ages or count of guests are invalid.

        :rtype: bool
        """

        return (
            self.bookings_repo.validate_cin_cout_dates(self.check_in_date, self.check_out_date) and
            self.bookings_repo.validate_rooms(self.rooms_params)
        )

    def process_booking_data(self):
        """
        Process the booking information from request arguments and formats them as required.

        > Gets guests adults and children information out of rooms params.
        """
        rooms_data = {}
        children_ages = []
        self.number_of_guests = 0
        self.number_of_children = 0

        for room_info in self.rooms_params:
            try:
                rooms_data['Room']
            except KeyError:
                rooms_data['Room'] = []

            single_room = collections.OrderedDict()

            single_room['Adults'] = int(room_info.get('a', 0))
            if room_info.get('c', 0) and room_info.get('c_ages', []):
                single_room['Children'] = room_info.get('c', 0)
                single_room['ChildAge'] = room_info.get('c_ages', [])

            rooms_data['Room'].append(single_room)
            self.number_of_guests += single_room.get('Adults', 0)
            self.number_of_children += single_room.get('Children', 0)
            children_ages.extend(single_room.get('ChildAge', []))

        self.children_ages = ','.join([str(c_age) for c_age in children_ages])
        self.rooms = rooms_data

    def book_request(self):
        """
        Books the request and then saves the request in DB.
        """

        self.booking_request_data = {
            'merchant_id': self.merchant_id,
            'outlet_id': self.outlet_id,
            'user_id': self.customer.get('user_id'),
            'email': self.customer_email,
            'salutation': self.customer_salutation,
            'first_name': self.customer_first_name,
            'family_name': self.customer_family_name,
            'mobile': self.customer_phone,
            'city': self.customer.get('city'),
            'country': self.customer.get('country'),
            'check_in_date': self.check_in_date,
            'check_out_date': self.check_out_date,
            'number_of_rooms': len(self.rooms),
            'number_of_guests': self.number_of_guests,
            'number_of_children': self.number_of_children,
            'additional_details': self.additional_details,
            'is_hww': True
        }
        self.enquiry_id = BookingRequest.save_booking_request(self.booking_request_data, self.logger)
        if self.enquiry_id:
            self.enquiry_number = "%09d" % self.enquiry_id
            self.enquiry_number = 'BK-{start}-{middle}-{last}'.format(
                start=self.enquiry_number[0:3],
                middle=self.enquiry_number[3:6],
                last=self.enquiry_number[6:9]
            )
            self.success_message = self.bookings_repo.SUCCESS_MESSAGE.format(bk_num=self.enquiry_number)

    def get_outlet_details(self):
        """
        Gets all the information of outlet against which the booking has been made.
        """
        outlet_info = Outlet.get_outlet_contact_info(self.outlet_id, self.locale)
        if outlet_info:
            if outlet_info.hotel:
                self.outlet_name = outlet_info.hotel
            elif outlet_info.outlet_name:
                outlet_name = outlet_info.outlet_name
                if '-' in outlet_name:
                    outlet_name = outlet_name.split('-')[0].strip()
                self.outlet_name = outlet_name

            self.outlet_country = outlet_info.country_name
            self.outlet_city = outlet_info.city_name
            self.outlet_email = outlet_info.email

    def update_booking_email(self):
        """
        Updates the email addresses of customer and merchant before sending.

        > Required for Al-Futaim:
        Since all customers from Al-Futaim have dummy emails in their profile table, we have to get it from AF user API
        and then send an email to that.

        """
        user_email = self.mail_repo.get_phone_users_email(
            auth_token=self.customer['session_token'],
            user_company=self.customer['company']
        )
        if user_email:
            self.booking_request_data['email'] = user_email

    def send_booking_email(self):
        """
        Sends the booking email to both merchant and customer.
        """
        booking_request_email_data = php_json_dumps({
            '{FIRST_NAME}': self.customer.get('name'),
            '{mobile}': self.customer.get('mobile'),
            '{email}': self.booking_request_data['email'],
            '{check_in_date}': self.booking_request_data['check_in_date'].strftime('%d/%m/%Y'),
            '{check_out_date}': self.booking_request_data['check_out_date'].strftime('%d/%m/%Y'),
            '{number_of_rooms}': self.booking_request_data['number_of_rooms'],
            '{additional_details}': self.booking_request_data['additional_details'],
            '{merchant_name}': self.outlet_name,
            '{hotel_name}': self.outlet_name,
            '{hotel_country}': self.outlet_country,
            '{hotel_city}': self.outlet_city,
            '{booking_enquiry_no}': self.enquiry_number,
            '{merchant_id}': self.merchant_id,
            '{outlet_id}': self.outlet_id
        })
        self.mail_repo.send_email(
            email_type_id=self.mail_repo.BOOKING_ENQUIRY_MERCHANT,
            email_data=php_json_dumps({}),
            email=self.outlet_email,
            language=self.messages_locale,
            priority=self.mail_repo.PRIORITY_MEDIUM,
            dump=False,
            optional_data=booking_request_email_data.decode(errors='ignore')
        )

        self.mail_repo.send_email(
            email_type_id=self.mail_repo.BOOKING_ENQUIRY_CUSTOMER,
            email_data=php_json_dumps({}),
            email=self.booking_request_data['email'],
            language=self.messages_locale,
            priority=self.mail_repo.PRIORITY_MEDIUM,
            dump=False,
            optional_data=booking_request_email_data.decode(errors='ignore')
        )

    def generate_final_response(self):
        """
        Generates final response.
        """
        self.send_response_flag = True
        self.status_code = 201
        self.response = {
            "code": self.status_code,
            "message": "success",
            "success": False,
            "data": {
                'is_enquiry_saved': self.enquiry_id > 0,
                'enquiry_number': self.enquiry_number,
                'title': self.bookings_repo.SUCCESS_TITLE,
                'message': self.success_message
            }
        }

    def generate_error_response(self):
        """
        Generates response in case of error e.g. booking failed.
        """
        self.send_response_flag = True
        self.response = {
            "code": self.status_code,
            "success": False,
            "data": {
                'title': "Something went wrong!",
                'message': self.response_msg
            }
        }

    def process_request(self, *args, **kwargs):
        """
        Handles request for Hww Booking Inquiry API.
        """
        self.initialize_repos()
        self.initialize_local_variables()
        if self.validate_booking_request():
            self.process_booking_data()
            self.book_request()
            if self.enquiry_id:
                self.get_outlet_details()
                self.update_booking_email()
                self.send_booking_email()
                self.generate_final_response()
            else:
                self.status_code = codes.service_unavailable
                self.response_msg = self.bookings_repo.BOOKING_ERROR_MSG
                self.generate_error_response()
        else:
            self.status_code = codes.unprocessable
            self.response_msg = self.bookings_repo.INVALID_DATES_MSG
            self.generate_error_response()
