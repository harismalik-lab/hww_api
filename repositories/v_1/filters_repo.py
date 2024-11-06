"""
Filters Repo module contains all the filters specific implementation and helper methods.
"""
from common.constants.icons import Icons
from models.attribute import Attribute


class FiltersRepo(object):
    """
    Filter section repository
    """
    AMENITIES_TITLE = "Hotel Facilities"
    FILTER_SECTION_INSTANT_BOOK = {
        "section_title": "Instant Book Only",
        "section_identifier": "instant_book_only",
        "api_param_name": "instant_book_only",
        "api_param_key": "show_instant_booking_hotels",
        "render_mode": "switch",
        "options": [{
            "api_param_value": "True",
            "api_param_key": "show_instant_booking_hotels",
            "title": "HWW Instant Booking"
        }]
    }

    FILTER_SECTION_TRAVEL_STYLE = {
        "section_title": "Travel Style",
        "section_identifier": "travel_style",
        "api_param_key": "offer_attributes",
        "selection_type": "multi_selection",
        "render_mode": "tags",
        "section_order_id": 1,
        "minimum_option_display": 6,
        "options": [
            {
                "api_param_value": "hww_brunch",
                "api_param_key": "offer_attributes",
                "title": "Stay & Brunch"
            },
            {
                "api_param_value": "hww_relax",
                "api_param_key": "offer_attributes",
                "title": "Stay & Relax"
            },
            {
                "api_param_value": "hww_dine",
                "api_param_key": "offer_attributes",
                "title": "Stay & Dine"
            },
            {
                "api_param_value": "hww_play",
                "api_param_key": "offer_attributes",
                "title": "Stay & Play"
            }
        ]
    }

    FILTER_SECTION_HOTEL_TYPES = {
        "section_title": "Hotel Type",
        "section_identifier": "hotel_type",
        "minimum_option_display": 5,
        "selection_type": "multi_selection",
        "api_param_key": "sub_categories",
        "render_mode": "tags",
        "section_order_id": 1,
        "options": [
            {
                "image_url_selected_web": Icons.STAR_RATING_SELECTED_WEB,
                "image_url_selected": Icons.STAR_SELECTED,
                "image_url_web": Icons.STAR_RATING_WEB,
                "image_url": Icons.STAR,
                "api_param_key": "sub_categories",
                "api_param_value": "5 Star",
                "order_id": 5,
                "title": "5",
                "listing_screen_title": "5 Star"
            },
            {
                "image_url_selected_web": Icons.STAR_RATING_SELECTED_WEB,
                "image_url_selected": Icons.STAR_SELECTED,
                "image_url_web": Icons.STAR_RATING_WEB,
                "image_url": Icons.STAR,
                "api_param_key": "sub_categories",
                "api_param_value": "4 Star",
                "order_id": 4,
                "title": "4",
                "listing_screen_title": "4 Star"
            },
            {
                "image_url_selected_web": Icons.STAR_RATING_SELECTED_WEB,
                "image_url_selected": Icons.STAR_SELECTED,
                "image_url_web": Icons.STAR_RATING_WEB,
                "image_url": Icons.STAR,
                "api_param_key": "sub_categories",
                "api_param_value": "3 Star",
                "order_id": 3,
                "title": "3",
                "listing_screen_title": "3 Star"
            },
            {
                "api_param_value": "B&B / Lodge",
                "api_param_key": "sub_categories",
                "title": "Bed & Breakfast"
            },
            {
                "api_param_value": "Hotel Apartments",
                "api_param_key": "sub_categories",
                "title": "Hotel Apartments"
            }
        ]
    }

    @classmethod
    def get_filter_section_amenities(cls, locale):
        """
        Get hotel facilities for filters hotel facilities section
        :param str locale: locale of the user
        :return Hotel facilities
        :rtype dict
        """
        filters = []
        filter_amenities = Attribute.get_facilities_for_amenities_section(locale)
        if filter_amenities:
            for index, amenity in enumerate(filter_amenities):
                options = {
                    "api_param_value": amenity.key,
                    "api_param_key": "merchant_attributes",
                    "title": amenity.name,
                    "image_url": amenity.v7_icon,
                    "image_url_selected": amenity.v7_icon_selected,
                    "order_id": index + 1
                }
                filters.append(options)

        return {
            "section_title": cls.AMENITIES_TITLE,
            "section_identifier": "hotel_amenities",
            "minimum_option_display": 6,
            "selection_type": "multi_selection",
            "render_mode": "tags",
            "section_order_id": 3,
            "collapsible": True,
            "show_more_button": True,
            "api_param_key": "merchant_attributes",
            "options": filters
        }
