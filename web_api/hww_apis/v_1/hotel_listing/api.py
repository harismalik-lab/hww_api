"""
Hww Hotel Listing API.
"""
import json

import requests
from flask import current_app, request

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.constants.colors import Colors
from common.utils.api_utils import multi_key_sort
from common.utils.authentication import get_company, get_current_customer
from models.mongo_models.searches import Searches
from models.mongo_models.viewed_hotels import ViewedHotels
from repositories.v_1.listing_repo import ListingRepo
from web_api.hww_apis.v_1.hotel_listing.validation import \
    hww_hotel_listing_api_parser


class HwwHotelListing(BasePostResource):
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='hotel_listing/hotel_listing_api.log',
        ),
        'name': 'hotel_listing'
    }
    required_token = True
    logger = None
    request_parser = hww_hotel_listing_api_parser

    def populate_request_arguments(self):
        """
        Populates the request arguments.
        """
        self.is_travel = self.request_args.get('is_travel')
        self.location_id = self.request_args.get('location_id')
        self.billing_country = self.request_args.get('billing_country')
        self.billing_city = self.request_args.get('billing_city')
        self.locale = self.request_args.get('language')
        self.lat = self.request_args.get('__lat')
        self.lng = self.request_args.get('__lng')
        self.device_lat = self.request_args.get('d_lat')
        self.device_lng = self.request_args.get('d_lng')
        self.radius = self.request_args.get('radius')
        self.is_map_search = self.request_args.get('is_map_search')
        self.platform = self.request_args.get('platform')
        self.offset = self.request_args.get('offset')
        self.sort = self.request_args.get('sort')
        self.app_version = self.request_args.get('app_version')
        self.category = self.request_args.get('category')
        self.limit = self.request_args.get('limit')
        self.currency = self.request_args.get('currency')
        self.show_instant_booking_hotels = self.request_args.get('show_instant_booking_hotels')
        self.merchant_attributes = (
            self.request_args.get('merchant_attributes[]') or
            self.request_args.get('merchant_attributes')
        )
        self.sub_categories = (
            self.request_args.get('sub_categories[]') or
            self.request_args.get('sub_categories')
        )
        self.offer_attributes = (
            self.request_args.get('offer_attributes[]') or
            self.request_args.get('offer_attributes')
        )
        self.query = self.request_args.get('query')
        self.search_type = self.request_args.get('search_type')
        self.is_recently_viewed_listing = self.request_args.get('is_recently_viewed_listing')
        self.screen_title = self.request_args.get('screen_title')

        self.map_lat = self.request_args.get('map_lat')
        self.map_lng = self.request_args.get('map_lng')

    def initialize_local_variables(self):
        """
        Initializes local variables to be used in a single request.

        is_current_location: True if the customer's current location is the same as the searched location.
        """
        self.customer = get_current_customer()
        self.data = {}
        self.outlets = {}
        self.is_current_location = self.listing_repo.is_current_location(
            lat=self.lat,
            lng=self.lng,
            search_type=self.search_type,
            search_query=self.query or self.billing_city or self.billing_country
        )
        self.is_destination_search = bool(self.billing_city or self.billing_country)

    def initialize_repos(self):
        """
        Initializes the different repos.
        """
        self.listing_repo = ListingRepo()

    def get_recently_viewed_hotel_ids(self):
        """
        Gets recently viewed hotel ids from MONGO.
        """

        self.recently_viewed_hotels = []
        if self.customer['is_user_logged_in']:
            self.recently_viewed_hotels = ViewedHotels.get_recently_viewed_hotels(
                customer_id=self.customer['customer_id']
            ).to_json()
            self.recently_viewed_hotels = json.loads(self.recently_viewed_hotels)

        return ','.join([str(hotel['outlet_id']) for hotel in self.recently_viewed_hotels])

    def get_outlets(self):
        """
        Getting hotel listing from Outlets API.
        """
        try:
            params = {
                "app_version": self.app_version,
                "category": self.category,
                "company": get_company(),
                "currency": self.currency,
                "language": self.locale,
                "lat": self.lat,
                "lng": self.lng,
                "location_id": self.location_id,
                "offset": self.offset,
                "limit": self.limit,
                "sort": self.sort,
                "show_instant_booking_hotels": self.show_instant_booking_hotels,
                "offer_attributes": self.offer_attributes,
                "merchant_attributes": self.merchant_attributes,
                "sub_categories": self.sub_categories,
                "is_travel": self.is_travel,
                "platform": self.platform,
                "billing_country": self.billing_country,
                "billing_city": self.billing_city,
                "search_by_dest_type": self.search_type
            }
            if self.is_recently_viewed_listing:
                recently_viewed_hotel_ids = self.get_recently_viewed_hotel_ids()
                if recently_viewed_hotel_ids:
                    params["o_ids"] = recently_viewed_hotel_ids
                    params.pop('search_by_dest_type')
                    params.pop('location_id')
                else:
                    return

            outlets = requests.get(
                current_app.config.get('OUTLETS_URL'),
                params=params,
                headers={"Authorization": request.environ.get('HTTP_AUTHORIZATION')}
            )
            if outlets.status_code == 200:
                self.outlets = json.loads(outlets.text)['data']
            else:
                raise Exception("Outlets service returned: {}".format(outlets.status_code))
        except Exception as e:
            self.logger.error('%s' % e)

    def add_screen_title_section(self):
        """
        Adds screen title section in Listing API response.
        """
        self.data['screen_title'] = self.screen_title

    def add_horizontal_menus_section(self):
        """
        Adds the horizontal menus section in the Listing API response.

        Horizontal menu in listing currently contains Sort / Filter / Map. These are passed through Filters API
        and changed via the listing API.
        """
        self.data["horizontal_menus"] = self.listing_repo.get_horizontal_menus(
            self.is_current_location,
            self.sort
        )

    def add_outlets_listing_section(self):
        """
        Adds the main listing section in the Listing API response.
        """
        section_title = self.listing_repo.LISTING_SECTION_TITLE.format(self.outlets.get("total_records"))

        self.data["listing_sections"] = [{
            "section_identifier": "search_similar_results",
            "section_title": section_title,
            "section_bg_color": Colors.WHITE,
            "section_title_color": Colors.DARK_GREY,
            "section_list": self.outlets_json
        }]

    def format_outlets(self):
        """
        Formats the outlet service response as required in the Listing API response.
        """
        self.outlets_json = self.listing_repo.format_outlets(
            is_current_location=self.is_current_location,
            outlets=self.outlets,
            currency=self.currency,
            is_destination_search=self.is_destination_search,
            logger=self.logger
        )

    def format_map_outlets(self):
        """
        Formats the outlets in case map-search is on.

        If map search is on, we only send out outlets which are in the radius provided in the request.
        """
        if self.is_map_search:
            self.outlets_json = self.listing_repo.get_map_outlets(
                self.radius,
                self.device_lat,
                self.device_lng,
                self.outlets_json
            )

    def sort_outlets(self):
        """
        Manually change the sorting of outlets if the sorting from outlet service does not fit.

        Following scenarios have been implemented.
        In case of recently viewed, we need to show the outlets in reverse order of when they were viewed.
        """
        if self.is_recently_viewed_listing and self.recently_viewed_hotels:
            for hotel in self.recently_viewed_hotels:
                for outlet in self.outlets_json:
                    if outlet['hotel_id'] == hotel['outlet_id']:
                        outlet['viewed_at'] = hotel['date_updated']['$date']
                        break

            self.outlets_json = multi_key_sort(self.outlets_json, ['-viewed_at'])

    def process_data(self):
        """
        This methods processes the data to be used in generating final response i.e. getting menus and listing data.
        """
        self.add_screen_title_section()
        self.add_horizontal_menus_section()
        self.get_outlets()
        self.format_outlets()
        self.sort_outlets()
        self.format_map_outlets()
        self.add_outlets_listing_section()

    def save_search(self):
        """
        Saves the search in MONGO for it to be accessible.
        """
        if self.customer["is_user_logged_in"] and self.query and self.search_type:
            Searches.save_recent_search(
                customer_id=self.customer["customer_id"],
                title=self.query,
                search_type=self.search_type,
                city=self.billing_city,
                country=self.billing_country
            )

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
            "code": self.status_code,
            "total_records": self.outlets.get("total_records", 0),
            "records_in_current_page": self.outlets.get("records_in_current_page"),
            "map_zoom_level": self.outlets.get("map_zoom_level"),
            "map_lat": self.map_lat,
            "map_lng": self.map_lng
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Handles request Hww Listing API.
        """
        self.initialize_repos()
        self.initialize_local_variables()
        self.process_data()
        self.save_search()
        self.generate_final_response()
