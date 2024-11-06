"""
Hww Home API.
"""
from flask import current_app

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.constants.icons import Icons
from common.constants.strings import CommonStrings
from common.utils.authentication import get_current_customer
from models.customer_order import CustomerOrder
from models.destinations import Destinations
from models.hb_order import HbOrder
from models.mongo_models.viewed_hotels import ViewedHotels
from repositories.v_1.home_repo import HomeRepo
from repositories.v_1.search_repo import SearchRepo
from web_api.hww_apis.v_1.home.validation import hww_home_api_parser


class HwwHome(BasePostResource):
    required_token = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='home/home_api.log',
        ),
        'name': 'home'
    }
    logger = None
    request_parser = hww_home_api_parser

    def populate_request_arguments(self):
        """
        Populates the request arguments.
        """
        self.locale = self.request_args.get('language')
        self.location_id = self.request_args.get('location_id')

    def initialize_local_variables(self):
        """
        Initializes local variables.
        """
        self.customer = get_current_customer()
        self.data = {
            "message": "",
            "title": self.home_repo.SCREEN_TITLE,
            "search_icon_image_url": Icons.SEARCH,
            "home_sections": [],
            "destination_list": []
        }

    def initialize_repos(self):
        """
        Initializes the different repos.
        """
        self.home_repo = HomeRepo()
        self.search_repo = SearchRepo()

    def add_destinations_section(self):
        """
        Adds destinations section in Home API.

        By default, five destinations will be shown on home screen and the sixth place will be a 'See all destinations'
        tile. When user clicks on the 'See All Destinations' tile, it'll return all destinations.
        """
        destinations = Destinations.get_home_destinations(locale=self.locale, limit=self.home_repo.DESTINATIONS_LIMIT)
        popular_destinations = []
        for destination in destinations:
            active_hotels_count = Destinations.get_active_hotels(location_id=destination.location_id)
            destination_obj = {
                'destination_id': destination.id,
                'item_title': destination.title,
                'item_image_url': destination.image_url,
                'item_description': self.home_repo.ACTIVE_HOTELS_COUNT.format(active_hotels=active_hotels_count),
                'deep_link': "",
                'should_open_deeplink': False,
                'lat': destination.lat,
                'lng': destination.lng,
                'api_params': {
                    "map_lat": destination.lat,
                    "map_lng": destination.lng,
                    "search_type": destination.type,
                }
            }
            if destination.type == self.search_repo.SEARCH_TYPE_CITY:
                destination_obj['api_params']['billing_city'] = destination.billing_city

            if destination.type == self.search_repo.SEARCH_TYPE_COUNTRY:
                destination_obj['api_params']['billing_country'] = destination.billing_country

            popular_destinations.append(destination_obj)

        popular_destinations.append(
            {
                "item_identifier": "item_show_more",
                "item_title": "See All Destinations",
                "item_description": "",
                "item_image_url": Icons.ARROW_SIGN,
                "should_open_deeplink": False,
                "deep_link": None,
                "api_params": {}
            }
        )

        self.data["home_sections"].append(
            {
                "section_identifier": "section_destinations",
                "accessory_section_image": "",
                "section_image": "",
                "see_all_button_title": CommonStrings.SEE_ALL,
                "section_title": self.home_repo.DESTINATIONS_TITLE,
                "clear_button_title": "",
                "section_list": popular_destinations
            }
        )
        destinations_list = self.home_repo.get_all_destination_data(locale=self.locale)
        if destinations_list:
            self.data["destination_list"] = destinations_list

    def add_bookings_section(self):
        """
        Adds bookings section in the Home API.

        This section is only shown if user has at least one confirmed or cancelled booking.
        """
        if self.customer['is_user_logged_in']:
            hww_module_id = current_app.config.get('HWW_MODULE_ID')
            user_booking = CustomerOrder.get_user_bookings_count(
                customer_id=self.customer.get('customer_id'),
                hww_module_id=hww_module_id
            ) or HbOrder.get_customer_getaways_bookings_count(
                customer_id=self.customer.get('customer_id')
            )
            if user_booking:
                self.data['home_sections'].append({
                    "section_identifier": "section_my_booking",
                    "section_title": self.home_repo.MY_BOOKINGS_TITLE,
                    "see_all_button_title": "",
                    "content_description": "",
                    "accessory_section_image": Icons.CALENDAR,
                    "section_image": Icons.RIGHT_BLUE,
                    "section_list": []
                })

    def add_recently_viewed_hotels_section(self):
        """
        Adds recently viewed hotels section in the Home API response.

        Recently viewed hotels section show only if a user has at least one recently viewed hotel.
        """
        if self.customer['is_user_logged_in']:
            recent_hotels = ViewedHotels.get_recently_viewed_hotels(
                customer_id=self.customer.get('customer_id'),
                get_count=True
            )

            if recent_hotels:
                self.data['home_sections'].append({
                    "section_identifier": "section_recent_hotels",
                    "accessory_section_image": "",
                    "section_image": "",
                    "see_all_button_title": "",
                    "section_title": self.home_repo.RECENT_HOTELS_TITLE,
                    "content_description": self.home_repo.RECENT_HOTELS_COUNT.format(recent_hotels_count=recent_hotels),
                    "section_list": [
                        {
                            "api_params": {
                                "is_recently_viewed_listing": True

                            }
                        }
                    ]

                })

    def add_travel_style_section(self):
        """
        Adds travel style section to Home API response.

        Travel style tiles are sections available for all users based on merchant attributes shown as per Travel
        requirements. For example: Stay & Brunch, Stay & Relax, Stay & Dine etc.
        """
        travel_style_tiles = self.home_repo.get_travel_style_tiles()
        if travel_style_tiles:
            self.data["home_sections"].append(
                {
                    "section_title": self.home_repo.YOUR_TRAVEL_STYLE_TITLE,
                    "section_identifier": "section_travel_style",
                    "accessory_section_image": "",
                    "section_image": "",
                    "see_all_button_title": "",
                    "section_list": travel_style_tiles,
                    "content_description": ""
                }
            )

    def add_curated_section(self):
        """
        Adds curated section to Home API response.

        Curated section on home screen is similar to more to Enjoy section on the Entertainer “home screen”
        e.g: Valentine Day Special.
        """
        curated_tiles = self.home_repo.get_curated_tiles()
        if curated_tiles:
            self.data["home_sections"].append(
                {
                    "section_title": self.home_repo.CURATED_TITLE,
                    "section_identifier": "section_curated_list",
                    "accessory_section_image": "",
                    "section_image": "",
                    "see_all_button_title": "",
                    "section_list": curated_tiles,
                    "content_description": ""
                }
            )

    def process_data(self):
        """
        Process the data of Hww Home API.
        """
        self.add_destinations_section()
        self.add_bookings_section()
        self.add_recently_viewed_hotels_section()
        self.add_travel_style_section()
        self.add_curated_section()

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
        Handles request Hww Home API.
        """
        self.initialize_repos()
        self.initialize_local_variables()
        self.process_data()
        self.generate_final_response()
