"""
Hww Hotel Details API Repo module contains all the details specific static data, implementation, and helper methods.
"""
import datetime
import math

from flask import current_app

from common.constants.colors import Colors
from common.constants.icons import Icons
from common.constants.values import URLs
from common.utils.api_utils import multi_key_sort
from models.exchange_rate import ExchangeRate


class HotelDetailsRepo(object):
    OUTLET_LIMIT = 60
    NO_OFFERS_FOUND_MSG = "No offers found."
    NO_MERCHANT_FOUND_MSG = "No merchant found."

    INQUIRE_FOR_RATES = 'Inquire For Rates'

    MAX_HOTEL_DESCRIPTION_CHARACTERS = 200

    WORK_BUTTON_TEXT = "How It Works"
    WORK_BUTTON_TEXT_COLOR = Colors.DARK_CYAN
    MORE_DETAIL_BUTTON_TITLE = "More Details"
    PACKAGES = "Packages"
    OFFERS = "Offers"
    DEFAULT_NUMBER_OF_AMENITIES_TO_SHOW = 9
    NUMBER_OF_PACKAGES_TO_SHOW = 3
    SHOW_MORE_DEALS_TITLE = "Show More Deals"
    SHOW_LESS_DEALS_TITLE = "Show Less Deals"
    SELECT_DEALS_BUTTON_TEXT = "Select Deals"

    TRAVEL_SECTION_TITLE = "Hotel Rules of Use"
    FEATURES_SECTION_TITLE = "Hotel Description"
    DESCRIPTION_SECTION_TITLE_2_FOR_1 = "About"
    DESCRIPTION_SECTION_TITLE_PKGS = "Hotel Description"

    EMPTY_VIEW_SECTION_TITLE = "An unknown error occurred."
    EMPTY_VIEW_SECTION_DESCRIPTION = "Looks like something went wrong when processing your request." \
                                     "Please check again later."
    INQUIRY_MESSAGE = "Please note that your reservation has not been finalised yet, this is a booking inquiry, and " \
                      "the hotel will be in touch with you shortly."

    WORK_POP_UP_VALUE = URLs.RULES_OF_USE_URL
    OFFERS_SECTION_IDENTIFIER = 'preview_offers'

    @classmethod
    def get_inquiry_data_config(cls):
        """
        Gets inquiry for rates form configurations.
        """
        return [
            {
                "section_accessory_left_button_image_url": Icons.MINUS_WHITE,
                "section_accessory_right_button_image_url": Icons.PLUS_WHITE,
                "section_identifier": "rooms",
                "section_title": "Room",
                "section_image_url": "",
                "section_collapsable": False,
                "section_min_value": 1,
                "section_max_value": 5,
                "section_min_message": "You cannot select less than 1 Room",
                "section_max_message": "You cannot add more than 12 Rooms",
                "options": [
                    {
                        "section_accessory_left_button_image_url": Icons.MINUS_WHITE,
                        "section_accessory_right_button_image_url": Icons.PLUS_WHITE,
                        "section_identifier": "adults",
                        "section_title": "Adult(s) 18+",
                        "section_collapsable": False,
                        "section_min_message": "You cannot select less than 1 Room",
                        "section_max_message": "You cannot add more than 12 Rooms",
                        "section_min_value": 1,
                        "section_max_value": 2
                    },
                    {
                        "section_accessory_left_button_image_url": Icons.MINUS_WHITE,
                        "section_accessory_right_button_image_url": Icons.PLUS_WHITE,
                        "section_identifier": "children",
                        "section_title": "Children",
                        "section_prefix": "Child",
                        "section_placeholder": "Select Age",
                        "section_dropdown_image_url": "",
                        "section_collapsable": True,
                        "section_min_message": "You cannot select less than 1 Room",
                        "section_max_message": "You cannot add more than 12 Rooms",
                        "section_default_error_message": "Please select valid child age",
                        "section_max_value": 2,
                        "section_min_value": 0,
                        "section_list_datasource": [
                            {
                                "title": "17 year old",
                                "value": 17
                            },
                            {
                                "title": "16 year old",
                                "value": 16
                            },
                            {
                                "title": "15 year old",
                                "value": 15
                            },
                            {
                                "title": "14 year old",
                                "value": 14
                            },
                            {
                                "title": "13 year old",
                                "value": 13
                            },
                            {
                                "title": "12 year old",
                                "value": 12
                            },
                            {
                                "title": "11 year old",
                                "value": 11
                            },
                            {
                                "title": "10 year old",
                                "value": 10
                            },
                            {
                                "title": "9 year old",
                                "value": 9
                            },
                            {
                                "title": "8 year old",
                                "value": 8
                            },
                            {
                                "title": "7 year old",
                                "value": 7
                            },
                            {
                                "title": "6 year old",
                                "value": 6
                            },
                            {
                                "title": "5 year old",
                                "value": 5
                            },
                            {
                                "title": "4 year old",
                                "value": 4
                            },
                            {
                                "title": "3 year old",
                                "value": 3
                            },
                            {
                                "title": "2 year old",
                                "value": 2
                            },
                            {
                                "title": "1 year old",
                                "value": 1
                            }
                        ]
                    }
                ]
            }
        ]

    @classmethod
    def get_hotel_packages(cls, outlet_id, merchant_id, currency):
        """
        Gets hotel packages from DB in case of Instant Booking.

        :param int outlet_id: ID of outlet of the instant booking merchant.
        :param int merchant_id: ID of instant booking merchant.
        :param str currency: Contains currency.
        :rtype: list
        """

        from models.package import Package
        packages_list = []

        packages = Package.get_packages(outlet_id, merchant_id)
        for package in packages:
            total_price = round(
                ExchangeRate.get_conversion_rate(
                    price=package.price,
                    currency_from=package.currency,
                    currency_to=currency
                )
            )
            discounted_price = round(
                ExchangeRate.get_conversion_rate(
                    price=package.discounted_price,
                    currency_from=package.discounted_currency,
                    currency_to=currency
                )
            )
            percentage_off = int(math.floor(((total_price - discounted_price) / total_price) * 100))

            package_type_text = "{p1} nights stay for {p2} adults".format(
                p1=package.no_of_nights,
                p2=package.no_of_adults
            )
            if package.no_of_childs:
                package_type_text = "{p1} and {p2} children".format(
                    p1=package_type_text,
                    p2=package.no_of_childs
                )

            checkout_params = {
                "package_type": "{} with hotel credits.".format(package_type_text),
                "package_title": package.short_name,
                "total_price": total_price,
                "outlet_id": outlet_id,
                "merchant_id": merchant_id,
                "room_type_id": package.room_type_id,
                "room_type": package.room_type_title,
                "deals_included": package.inclusions,
                "deal_terms": package.terms,
                "cancellation_policy": package.cancellation_notes,
                "off_percentage": percentage_off,
                "discounted_price": discounted_price
            }
            is_non_discount_pkg = (
                package.price == package.discounted_price and
                package.currency == package.discounted_currency
            )

            if is_non_discount_pkg:
                # In case of non-discount packages, the app treats discounted price as actual price as to not
                # show the struck-through text.
                total_price, percentage_off = 0, 0

            package_info = {
                "booking_cart_url": current_app.config.get('BOOKING_CART_URL'),
                "is_best_offer": package.is_best_offer,
                "is_2_for_1": package.is_2_for_1,
                "more_detail_button_title": cls.MORE_DETAIL_BUTTON_TITLE,
                "room_id": package.room_type_id,
                "best_offer_tag_image_url": Icons.BEST_OFFER,
                "offer_image_url": Icons.IS_2_FOR_1 if package.is_2_for_1 else "",
                "offer_title": package.short_name,
                "stay_duration_text": "{}.".format(package_type_text),
                "offer_validity_text": "Valid before {p1}".format(
                    p1=datetime.datetime.strftime(package.validity_date, '%d %B %Y')
                ),
                "actual_price": "{p1} {p2}".format(p1=currency, p2=total_price) if total_price else '',
                "actual_price_value": math.ceil(total_price) if total_price else None,
                "discounted_price": "{p1} {p2}".format(p1=currency, p2=discounted_price),
                "discounted_price_value": math.ceil(discounted_price),
                "percentage_off_title": '',
                "percentage_off_title_bg": ''
            }
            if percentage_off:
                checkout_params['off_percentage'] = percentage_off
                package_info.update({
                    "percentage_off_title": "{}% off".format(percentage_off),
                    "percentage_off_title_bg": Colors.RED,
                })

            package_info["booking_cart_params"] = checkout_params
            packages_list.append(package_info)

        sort_order = ['-is_best_offer', 'discounted_price_value']
        return multi_key_sort(packages_list, sort_order)

    @property
    def required_merchant_fields(self):
        return (
            'id',
            'name',
            'email',
            'website',
            'merchant_pin',
            'logo_url',
            'logo_small_url',
            'logo_offer_url',
            'logo_offer_small_url',
            'photo_url',
            'photo_small_url',
            'hero_urls',
            'hero_small_urls',
            'p3_hero_image_non_retina',
            'p3_360_degree_image',
            'hero_images_360',
            'is_opted_in_for_360_image',
            'is_opted_in_for_360_image',
            'booking_request',
            'booking_link',
            'sponsor_title',
            'offer_instruction_message',
            'is_favourite',
            'is_tutorial',
            'is_pingable',
            'dc_prospect_enabled'
        )
