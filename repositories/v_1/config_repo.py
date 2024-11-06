"""
Hww Config Repo module contains all the listing specific static data, implementation, and helper methods.
"""

from common.constants.icons import Icons
from models.currency import Currency


class ConfigRepo(object):
    SDK_DEFAULT_CURRENCY = 'AED'

    UI_CONFIG = {
        "sdk_default_currency": SDK_DEFAULT_CURRENCY,
        "placeholder_image": Icons.HOTEL_PLACEHOLDER,
        "edit_icon": Icons.EDIT,
        "close_icon_dark": Icons.CLOSE_DARK,
        "drop_arrow_light": Icons.DROP_ARROW_LIGHT,
        "drop_arrow_dark": Icons.DROP_ARROW_DARK,
        "back_navigation_arrow": Icons.BACK_NAVIGATION_ARROW,
        "search_icon_dark": Icons.SEARCH_DARK,
        "location_dark_icon": Icons.LOCATION_DARK
    }

    def get_user_selected_currency(self, currency):
        """
        Gets the user selected currency
        :param currency
        :rtype: dict
        """
        currency_info = Currency.get_user_currency(currency)
        if not currency_info:
            return {}
        return {
            "translated_currency": currency_info.translated_currency,
            "id": currency_info.id,
            "currency_id": currency_info.currency_id,
            "name": currency_info.name
        }
