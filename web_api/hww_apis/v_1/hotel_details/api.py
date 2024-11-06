"""
Hww Hotel Details API.
"""
import json

import requests
from flask import current_app, request
from requests import codes

from app_configurations.settings import HWW_LOG_PATH
from common.base_resource import BasePostResource
from common.constants.colors import Colors
from common.constants.icons import Icons
from common.constants.strings import CommonStrings
from common.constants.values import CommonValues
from common.utils.authentication import get_current_customer
from models.merchant_attribute import MerchantAttribute
from models.merchant_attributes_travel import MerchantAttributesTravel
from models.mongo_models.searches import Searches
from models.mongo_models.viewed_hotels import ViewedHotels
from repositories.v_1.details_repo import HotelDetailsRepo
from web_api.hww_apis.v_1.hotel_details.validation import \
    hww_hotel_details_api_parser


class HwwDetails(BasePostResource):
    required_token = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=HWW_LOG_PATH,
            file_path='hotel_details/hotel_details_api.log',
        ),
        'name': 'hotel_details'
    }
    logger = None
    request_parser = hww_hotel_details_api_parser

    def populate_request_arguments(self):
        """
        Populates the request arguments.
        """
        self.locale = self.request_args.get('language')
        self.location_id = self.request_args.get('location_id')
        self.offset = self.request_args.get('offset')
        self.limit = self.request_args.get('limit')
        self.device_model = self.request_args.get('device_model')
        self.timezone = self.request_args.get('timezone')
        self.platform = self.request_args.get('__platform')

        self.app_version = self.request_args.get("app_version")
        self.merchant_id = self.request_args.get('merchant_id')
        self.outlet_id = self.request_args.get('outlet_id')
        self.is_hww_instant_booking = self.request_args.get('is_hww_instant_booking')
        self.company = self.request_args.get('company')
        self.currency = self.request_args.get('currency')
        self.query = self.request_args.get('query')
        self.search_type = self.request_args.get('search_type')

    def initialize_repos(self):
        """
        Initializes the different repos.
        """
        self.details_repo = HotelDetailsRepo()

    def initialize_local_variables(self):
        """
        Initializes the local variables.
        """
        self.customer = get_current_customer()
        self.data = {}
        self.hotel_details = {}
        self.merchant_response_data = {}
        self.hotel_details_sections = []
        self.merchant_offers = []

    def add_hotel_header_section(self):
        """
        Adds header section in hotel details.
        """
        header_section = {
            "section_identifier": "header",
            "section_title": "",
            "hotel_logo_image_url": self.merchant_response_data.get("logo_offer_url"),
            "hotel_name": self.merchant_response_data.get('name'),
            "hotel_type": "",
            "hotel_rating": self.merchant_response_data.get("hotel_rating"),
            "hotel_location": self.outlet_data.get("human_location") or ""
            # "trip_adv_webview_link": self.outlet_data.get('trip_adv_webview_link'),
            # "trip_adv_rating": 0,
            # "trip_adv_rating_image_url": '',
            # "trip_adv_reviews": '',
        }
        # if self.outlet_data.get('tripadvisor_rating'):
        #     header_section["trip_adv_rating_image_url"] = self.outlet_data["trip_adv_rating_image"]
        #     header_section["trip_adv_rating"] = "{}".format(self.outlet_data["tripadvisor_rating"])
        #
        # if self.outlet_data.get('trip_adv_rating_reviews_count'):
        #     header_section["trip_adv_reviews"] = "{} reviews".format(self.outlet_data["trip_adv_rating_reviews_count"])

        self.hotel_details_sections.append(header_section)

    def add_outlet_info_section(self):
        """
        Adds outlet info section in hotel details.
        """
        self.hotel_details_sections.append({
            "section_identifier": "outlet_selection",
            "section_title": ""
        })

    def add_hotel_location_section(self):
        """
        Adds hotel location section in HWW hotel details response.
        """

        hotel_location_parts = [
            self.outlet_data.get('human_location'),
            self.outlet_data.get('hotel'),
            self.outlet_data.get('mall'),
            self.outlet_data.get('neighborhood')
        ]
        hotel_location_text = ", ".join(filter(None, hotel_location_parts))

        location_section = {
            "section_identifier": "location",
            "section_title": "",
            "hotel_lat": self.outlet_data.get('lat'),
            "hotel_lng": self.outlet_data.get('lng'),
            "map_zoom_level": CommonValues.MAP_ZOOM_LEVEL,
            "location_pin_image_url": Icons.MAP,
            "hotel_location_text": hotel_location_text
        }

        self.hotel_details_sections.append(location_section)

    def add_hotel_amenities_section(self):
        """
        Adds HWW hotel amenities section in response.
        """
        amenities_section_list = []
        amenities = MerchantAttribute.get_amenities_by_locale(
            locale=self.locale,
            category=CommonValues.TRAVEL_CATEGORY_ID
        )
        merchant_attributes_travel = MerchantAttributesTravel.get_attributes(self.merchant_id)

        for amenity in amenities:
            if getattr(merchant_attributes_travel, amenity.attribute_key) not in [0, -1]:
                amenities_section_list.append({
                    'title': amenity.attribute_name,
                    'value': amenity.image_url or Icons.DEFAULT_AMENITY
                })

        self.hotel_details_sections.append({
            "section_identifier": "amenities",
            "section_title": "Amenities",
            "section_sub_title": "",
            "collapse_button_image_url": Icons.THREE_DOTS,
            "expand_button_image_url": Icons.THREE_DOTS,
            "should_show_expand_button": True,
            "expand_max_limit": self.details_repo.DEFAULT_NUMBER_OF_AMENITIES_TO_SHOW,
            "amenities": amenities_section_list,
        })

    def add_hotel_regular_offers_section(self):
        """
        Adds regular offers e.g. 2-for-1 in case of non instant booking section.

        """
        for offer in self.merchant_offers:
            offer.update({
                "section_identifier": "offers",
                "section_title": self.details_repo.OFFERS,
                "section_sub_title": "",
                "show_how_it_works_button": True,
                "how_it_works_button_text": self.details_repo.WORK_BUTTON_TEXT,
                "how_it_works_button_text_color": self.details_repo.WORK_BUTTON_TEXT_COLOR,
                "how_it_work_popup": {
                    "title": self.details_repo.TRAVEL_SECTION_TITLE,
                    "value": self.details_repo.WORK_POP_UP_VALUE
                },
                'select_deal_button_text': self.details_repo.INQUIRE_FOR_RATES,

            })
            for offer_display in offer['offers_to_display']:
                offer_display.update({
                    'smiles_earn_value': '',
                    'smiles_burn_value': '',
                    'is_show_smiles': False,
                    'hhs': '',
                })
                try:
                    if (
                        offer_display.get('additional_details') and
                        offer_display.get('additional_details')[0] and
                        offer_display['redeemability'] == 2
                    ):
                        offer_display['additional_details'][0]['image'] = Icons.VOUCHER_DOT
                except Exception:
                    pass

                # Removing the smiles object.
                try:
                    if (
                        offer_display.get('additional_details') and
                        offer_display.get('additional_details')[2]
                    ):
                        del offer_display['additional_details'][2]
                except IndexError:
                    pass
                try:
                    if (
                        offer_display.get('additional_details') and
                        offer_display.get('additional_details')[1] and
                        offer_display['redeemability'] == 2
                    ):
                        offer_display['additional_details'][1]['image'] = Icons.VOUCHER_DOT
                except Exception:
                    pass

            self.hotel_details_sections.append(offer)

    def add_hotel_packages_section(self):
        """
        Adds the hotel packages section in case of HWW instant booking merchant.

        In case, no valid packages are available, adds regular offers.
        """

        packages_list = self.details_repo.get_hotel_packages(
            outlet_id=self.outlet_id,
            merchant_id=self.merchant_id,
            currency=self.currency
        )
        if packages_list:
            self.hotel_details_sections.append({
                "section_identifier": "packages",
                "section_title": self.details_repo.PACKAGES,
                "number_of_packages_to_show": self.details_repo.NUMBER_OF_PACKAGES_TO_SHOW,
                "show_more_button_title": self.details_repo.SHOW_MORE_DEALS_TITLE,
                "show_less_button_title": self.details_repo.SHOW_LESS_DEALS_TITLE,
                "packages": packages_list
            })
        else:
            self.is_hww_instant_booking = False
            self.add_hotel_regular_offers_section()
            self.add_inquiry_data_section()

    def add_is_hww_instant_booking_section(self):
        """
        Adds the instant hww instant booking section to show which sort of offers are we showing in the details
        section.

        This section helps the APP team decide which view they want to show to the customer in case of packages and
        regular inquire offers.
        """

        self.data['is_hww_instant_booking'] = int(self.is_hww_instant_booking)

    def add_hotel_description_section(self):
        """
        Adds hotel description section in HWW hotel details API response.
        """
        if self.merchant_response_data.get('description'):
            description = self.merchant_response_data['description']
            if len(description) > self.details_repo.MAX_HOTEL_DESCRIPTION_CHARACTERS:
                short_description = "{}...".format(description[:self.details_repo.MAX_HOTEL_DESCRIPTION_CHARACTERS])
            else:
                short_description = description

            feature_section = {
                "section_identifier": "features",
                "section_title": self.details_repo.FEATURES_SECTION_TITLE,
                "section_sub_title": "",
                "detail_description": description
            }

            description_section = {
                "section_identifier": "details",
                "short_description": short_description,
                "number_of_characters_to_show": self.details_repo.MAX_HOTEL_DESCRIPTION_CHARACTERS,
                "read_more_text": "Read More",
                "read_more_text_color": Colors.BLUE,
                "details": [feature_section]
            }
            if self.is_hww_instant_booking:
                description_section["section_title"] = self.details_repo.DESCRIPTION_SECTION_TITLE_PKGS
            else:
                description_section["section_title"] = self.details_repo.DESCRIPTION_SECTION_TITLE_2_FOR_1

            self.hotel_details_sections.append(description_section)
        else:
            self.add_empty_view_section()

    def add_empty_view_section(self):
        """
        Adds empty view section in HWW details response.
        """
        self.hotel_details_sections.append({
            "section_identifier": "empty_view",
            "section_title": self.details_repo.EMPTY_VIEW_SECTION_TITLE,
            "section_description": self.details_repo.EMPTY_VIEW_SECTION_DESCRIPTION
        })

    def get_hotel_details_sections(self):
        """
        Adds all sections of HWW hotel details to API response.
        """
        self.add_hotel_header_section()
        self.add_outlet_info_section()
        self.add_hotel_location_section()
        self.add_hotel_amenities_section()
        if self.is_hww_instant_booking:
            self.add_hotel_packages_section()
        else:
            self.add_hotel_regular_offers_section()
            self.add_inquiry_data_section()

        self.add_hotel_description_section()
        self.add_is_hww_instant_booking_section()

    def add_merchant_section(self):
        """
        Adding merchant section in hotel detail.

        > This section contains duplicate data already scattered in API response but the APP team required a single
        object so we added this section in JSON.

        """
        merchant_keys = self.details_repo.required_merchant_fields
        merchant_section = {
            merchant_key: self.merchant_response_data.get(merchant_key) for merchant_key in merchant_keys
        }
        self.data['hotel_detail']['merchant'] = merchant_section

    def set_analytics_type(self):
        """
        Set analytics type in hotel detail section.
        """
        if self.is_hww_instant_booking:
            self.data['hotel_detail']['analytics_source_type'] = "connected"
        else:
            self.data['hotel_detail']['analytics_source_type'] = "ent"

    def process_hotel_details(self):
        """
        Process the hotel detail section of Hww Hotel Details API response.
        """
        self.outlet_data = self.merchant_response_data.get("outlets")[0]
        self.get_hotel_details_sections()
        self.data['hotel_detail'] = {
            "hotel_detail_sections": self.hotel_details_sections,
            "select_deal_button_text": self.details_repo.SELECT_DEALS_BUTTON_TEXT,
            "select_deal_button_text_color": Colors.WHITE,
            "select_deal_button_bg_color": Colors.BLUE,
            "hotel_images": self.merchant_response_data['hero_urls'],
            "hotel_id": self.outlet_id,
            "hotel_name": self.merchant_response_data.get('name'),
            'outlets': self.merchant_response_data.get('outlets')
        }
        self.add_merchant_section()
        self.set_analytics_type()

    def get_merchant_info(self):
        """
        Gets merchant info from DB.

        Currently setting hww instant booking flag in case it comes zero.

        """
        if not self.is_hww_instant_booking:
            from models.merchant import Merchant
            self.is_hww_instant_booking = Merchant.get_by_id(self.merchant_id).hww_instant_booking

    def get_merchant_data(self):
        """
        Gets merchant data based on company.

        If it's a White-Label company it uses a PHP call. If it's entertainer, it uses a Python API call.
        """
        try:
            request_data = {}
            request_data.update(self.request_args)
            request_data.update({
                'session_token': self.customer.get('session_token'),
                'platform': self.platform,
                '__platform': self.platform,
                'category': CommonStrings.CATEGORY_TRAVEL,
                '__category': CommonStrings.CATEGORY_TRAVEL,
                '__i': self.customer.get('customer_id'),
                '__sid': self.customer.get('id'),
                '_format': 'json',
                'location_id': self.location_id,
                'app_version': self.app_version,
                'language': self.locale,
                'sort': 'default',
                'redeemability': 'redeemable_reusable',
                'offset': self.offset,
                'limit': self.limit,
                'device_model': self.device_model,
                'currency': self.currency,
                'outlet_id': self.outlet_id,
            })
            response = requests.get(
                current_app.config.get('MERCHANT_URL').format(merchant_id=self.merchant_id),
                params=request_data,
                headers={"Authorization": request.environ.get('HTTP_AUTHORIZATION')},
            )
            if response.status_code == 200:
                self.merchant_response_data = json.loads(response.text)['data']['merchant']
        except Exception as e:
            self.logger.exception(e)

    def add_inquiry_data_section(self):
        """
        Adds inquiry data section in case of non instant booking packages.
        """
        self.data['inquiry_data'] = {
            "merchant_email": self.outlet_data.get('email'),
            "hotel_id": self.outlet_data.get('id'),
            "hotel_name": self.merchant_response_data.get('name'),
            "location_id": self.outlet_data.get('location_id'),
            "configuration": self.details_repo.get_inquiry_data_config(),
            "cross_image_url": Icons.CROSS,
            "calendar_image_url": Icons.CALENDAR_BLANK,
            "rooms_image_url": Icons.ROOMS,
            "people_image_url": Icons.USER,
            "message": self.details_repo.INQUIRY_MESSAGE,
            "country_drop_down_image_url": Icons.COUNTRY_DROP_DOWN,
        }

    def generate_final_response(self):
        """
        Generates the final response in case of success.
        """
        self.send_response_flag = True
        self.status_code = codes.ok
        self.response = {
            "message": '',
            "success": True,
            "data": self.data,
            "code": self.status_code
        }
        return self.send_response(self.response, self.status_code)

    def generate_error_response(self):
        """
        Generates error response in case of some failure. For example, no merchant passed from app or no offers present.
        """
        self.send_response_flag = True
        self.response = {
            "success": False,
            "message": self.response_msg,
            "data": {},
            "code": self.status_code
        }
        return self.send_response(self.response, self.status_code)

    def save_search(self):
        """
        Saves the hotels in MONGO for it to be accessible.
        """
        if self.customer["is_user_logged_in"]:
            ViewedHotels.save_viewed_hotel(
                customer_id=self.customer["customer_id"],
                outlet_id=self.outlet_id,
                merchant_id=self.merchant_id,
                title=self.merchant_response_data.get('name'),
            )
            if self.query and self.search_type:
                Searches.save_recent_search(
                    customer_id=self.customer["customer_id"],
                    outlet_id=self.outlet_id,
                    merchant_id=self.merchant_id,
                    title=self.merchant_response_data.get('name'),
                    search_type=self.search_type
                )

    def get_merchant_offers_data(self):
        """
        Gets merchant offer data from service response.
        """

        for section in self.merchant_response_data.get('sections', []):
            if section['identifier'] == self.details_repo.OFFERS_SECTION_IDENTIFIER:
                self.merchant_offers = section.get('offers')

    def process_request(self, *args, **kwargs):
        """
        Handles request for Hww HotelDetails API.
        """

        self.initialize_repos()
        self.initialize_local_variables()

        if self.merchant_id:
            self.get_merchant_info()
            self.get_merchant_data()
            self.get_merchant_offers_data()
            if self.merchant_offers:
                self.process_hotel_details()
            else:
                self.status_code = codes.no_response
                self.response_msg = self.details_repo.NO_OFFERS_FOUND_MSG
                return self.generate_error_response()
        else:
            self.status_code = codes.precondition_required
            self.response_msg = self.details_repo.NO_MERCHANT_FOUND_MSG
            return self.generate_error_response()

        self.save_search()
        self.generate_final_response()
