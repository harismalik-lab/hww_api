"""
Listing Repo module contains all the listing specific static data, implementation, and helper methods.
"""
import math
from copy import deepcopy

import pycountry
from fuzzywuzzy import fuzz
from geopy.geocoders import Nominatim
from shapely.geometry import Point

from common.constants.icons import Icons
from common.utils.api_utils import is_valid_coordinates
from repositories.v_1.search_repo import SearchRepo


class ListingRepo(object):
    INSTANT_BOOKING = 'Instant Booking'
    INQUIRE_FOR_RATES = 'Inquire For Rates'
    LISTING_SECTION_TITLE = '{} Hotels'
    MINIMUM_FUZZY_MATCH_RATIO = 90

    SORT_OPTIONS = [
        {
            "key": "default",
            "selected": False,
            "title": "Recommended for you"
        },
        {
            "key": "nearest_to_me",
            "selected": False,
            "title": "Nearest to me"
        },
        {
            "key": "best_reviewed",
            "selected": False,
            "title": "Best reviewed"
        },
        {
            "key": "most_reviewed",
            "selected": False,
            "title": "Most reviewed"
        }
    ]

    BASE_HORIZONTAL_MENU = [
        {
            "menu_type": 1,
            "menu_image_url": Icons.MENU_SORT,
            "menu_identifier": "menu_sort",
            "background_color": "",
            "menu_title": "Sort",
            "options": [],
            "text_color": ""
        },
        {
            "menu_image_url": Icons.MENU_FILTER,
            "menu_title": "Filter",
            "background_color": "",
            "text_color": "",
            "menu_type": 2,
            "menu_identifier": "menu_filter"
        },
        {
            "menu_image_url": Icons.MENU_MAP,
            "menu_title": "Map",
            "background_color": "",
            "text_color": "",
            "menu_type": 3,
            "menu_identifier": "menu_map"
        },
        {
            "menu_image_url": Icons.MENU_LIST,
            "menu_title": "List",
            "background_color": "",
            "text_color": "",
            "menu_type": 4,
            "menu_identifier": "menu_list"
        }
    ]

    @classmethod
    def is_current_location(cls, lat, lng, search_type, search_query):
        """
        Returns if current location of a customer is the same as the searched location.

        We use fuzzywuzzy to match current location with outlet billing city or country based on search type.

        :rtype: bool
        """

        if lat and lng:
            try:
                geolocator = Nominatim(user_agent="ent_travel")
                location = geolocator.reverse(
                    "{latitude}, {longitude}".format(latitude=lat, longitude=lng),
                    language='en'
                )
            except Exception:
                location = None

            if location:
                usr_location = ''
                usr_location_address = getattr(location, 'raw', {}).get('address', {})

                if search_type == SearchRepo.SEARCH_TYPE_CITY:
                    usr_location = (
                        usr_location_address.get('city', '') or
                        usr_location_address.get('state', '') or
                        usr_location_address.get('county', '')
                    )
                elif search_type == SearchRepo.SEARCH_TYPE_COUNTRY:
                    usr_country = usr_location_address.get('country', '')
                    usr_country_info = pycountry.countries.search_fuzzy(usr_country)
                    if usr_country_info:
                        usr_location = usr_country_info[0].alpha_2

                if usr_location and search_query:
                    match_ratio = fuzz.ratio(usr_location.lower(), search_query.lower())
                    return match_ratio >= cls.MINIMUM_FUZZY_MATCH_RATIO

        return False

    def get_horizontal_menus(self, is_current_location, sort_option):
        """
        This method returns the horizontal menus required in listing API response.

        :param is_current_location: If the current location is same as the searched location.
        :param str sort_option: Sort option selected by the user.
        :rtype: list
        """
        horizontal_menus = deepcopy(self.BASE_HORIZONTAL_MENU)
        sort_options = deepcopy(self.SORT_OPTIONS)

        if not is_current_location:
            sort_options.pop(1)

        for option in sort_options:
            if sort_option == option['key']:
                option['selected'] = True
                break

        horizontal_menus[0]['options'] = sort_options

        return horizontal_menus

    def format_outlets(self, **kwargs):
        """
        This methods converts the Outlets API response into desired json format.
        :rtype: list
        """
        final_outlets = []
        outlets = kwargs.get('outlets', {})
        is_current_location = kwargs.get('is_current_location', False)
        is_destination_search = kwargs.get('is_destination_search', False)
        if outlets:
            currency = kwargs.get('currency')
            logger = kwargs.get('logger')
            for outlet in outlets['outlets']:
                try:
                    outlet_data = {
                        "hotel_id": outlet["id"],
                        "hotel_title": outlet["hotel"],
                        "hotel_rating": outlet["hotel_rating"] or 0,
                        "hotel_logo_url": outlet["merchant"]["logo_small_url"],
                        "lng": outlet["lng"],
                        "lat": outlet["lat"],
                        "merchant_id": outlet["merchant"]["id"],
                        "images_url": outlet["images_url"],
                        "analytics_source_type": "connected",
                        "is_connected": outlet["is_hww_instant_booking"],
                        "billing_city": outlet.get('billing_city', ''),
                        "billing_country": outlet.get('billing_country', ''),
                        "hotel_subtitle": '',
                        "hotel_offer_title": '',
                        "hotel_offer_price_text": '',
                        "hotel_offer_night_text": '',
                        "hotel_offer_description": '',
                        # "trip_adv_reviews": '',
                        # "trip_adv_rating_image_url": '',
                        # "trip_adv_rating": 0,
                        "web_api_params": {},
                        "api_params": {
                            'merchant_id': outlet["merchant"]["id"],
                            'outlet_id': outlet["id"],
                            'is_hww_instant_booking': outlet["is_hww_instant_booking"]
                        }
                    }

                    # if outlet['ta_rating']:
                    #     outlet_data["trip_adv_rating_image_url"] = outlet["ta_rating_img_url"]
                    #     outlet_data["trip_adv_rating"] = "{}".format(outlet["ta_rating"])
                    #
                    # if outlet['ta_reviews_count']:
                    #     outlet_data["trip_adv_reviews"] = "{} reviews".format(outlet["ta_reviews_count"])

                    if is_current_location:
                        if outlet['neighborhood']:
                            outlet_data['hotel_subtitle'] = outlet['neighborhood']
                            if outlet.get('distance'):
                                outlet_data['distance'] = "{} km".format(math.ceil(outlet['distance'] / 1000))

                    if not is_destination_search:
                        if outlet['billing_city'] or outlet['billing_country']:
                            city_country = ", ".join(filter(None, [outlet['billing_city'], outlet['billing_country']]))
                            outlet_data['hotel_subtitle'] = city_country

                    if outlet['hww_title'] == self.INQUIRE_FOR_RATES:
                        outlet_data.update({
                            "is_hww_instant_booking": 0,
                            "hotel_offer_title": self.INQUIRE_FOR_RATES,
                            "hotel_offer_price_text": self.INQUIRE_FOR_RATES,
                            "hotel_offer_image_url": Icons.IS_2_FOR_1,
                        })
                    else:
                        no_of_nights = int(outlet.get("no_of_nights", 0) or 0)
                        price_str = 'From {} {}'.format(currency, outlet['package_price'])
                        night_str = ''
                        if no_of_nights == 1:
                            night_str = 'for {} Night'.format(no_of_nights)
                        elif no_of_nights > 1:
                            night_str = 'for {} Nights'.format(no_of_nights)

                        price = '{price_str} {night_str}'.format(price_str=price_str, night_str=night_str)

                        outlet_data.update({
                            "is_hww_instant_booking": 1,
                            "hotel_offer_title": price,
                            "hotel_offer_price_text": price_str,
                            "hotel_offer_night_text": night_str,
                            "hotel_offer_description": self.INSTANT_BOOKING
                        })

                    final_outlets.append(outlet_data)
                except KeyError as e:
                    logger.error(e)

        return final_outlets

    @staticmethod
    def get_map_outlets(radius, point_latitude, point_longitude, outlets):
        """
        Filters out the outlets as per required in a map of a certain radius.

        Calculates the outlets present in a certain radius around the given latitude and longitude values.
        :param int radius: Radius of the map.
        :param point_latitude: The latitude of the point around which the radius is made.
        :param point_longitude: The longitude of the point around which the radius is made.
        :param outlets: The total outlets from which the results are supposed to be filtered from.
        :rtype: list
        """
        outlets = list(filter(lambda x: is_valid_coordinates(x['lat'], x['lng']), outlets))
        if outlets:
            polygon_radius = radius / 100000
            if not (
                point_latitude and
                point_longitude and
                abs(float(point_latitude)) > 0 and
                abs(float(point_longitude)) > 0
            ):
                point_latitude = outlets[0]['lat']
                point_longitude = outlets[0]['lng']

            polygon = Point(float(point_longitude), float(point_latitude)).buffer(float(polygon_radius))
            outlets = list(filter(lambda x: polygon.contains(Point(float(x['lng']), float(x['lat']))), outlets))

        return outlets
