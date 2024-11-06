"""
Home Repo module contains all the Home API specific implementation and helper methods.
"""
from models.destinations import Destinations
from models.home_section import HomeSection


class HomeRepo(object):

    SCREEN_TITLE = 'Entertainer Travel'
    DESTINATIONS_TITLE = 'Destinations'
    YOUR_TRAVEL_STYLE_TITLE = 'Your travel style'
    CURATED_TITLE = 'Curated for you'
    MY_BOOKINGS_TITLE = 'My Bookings'
    RECENT_HOTELS_TITLE = 'Recently viewed hotels'
    RECENT_HOTELS_COUNT = '{recent_hotels_count} Hotels'
    ACTIVE_HOTELS_COUNT = '{active_hotels} Hotels'
    DESTINATIONS_LIMIT = 5

    @staticmethod
    def get_travel_style_tiles():
        """
        Gets travel style tiles from home section table.
        :rtype: list
        """
        travel_tiles = HomeSection.get_travel_style_section()
        travel_style_list = []
        for item in travel_tiles:
            travel_style_tile = {
                "entity_id": item.id,
                'item_title': item.title,
                'item_image_url': item.image_url,
                'api_param_key': 'offer_attributes',
                'api_param_value': item.description,
                'api_params': {
                    'offer_attributes': [item.title],
                    'screen_title': item.title
                }
            }
            travel_style_list.append(travel_style_tile)
        return travel_style_list

    @staticmethod
    def get_curated_tiles():
        """
        Gets curated tiles from home section table.
        :rtype: list
        """
        curated_tiles = HomeSection.get_curated_section()
        curated_section_list = []
        for item in curated_tiles:
            curated_section_tile = {
                "entity_id": item.id,
                'item_title': item.title,
                'item_image_url': item.image_url,
                'deep_link': item.deep_link,
            }
            curated_section_list.append(curated_section_tile)
        return curated_section_list

    @staticmethod
    def get_all_destination_data(locale):
        """
        Sets all the destinations data. Section title contains the region name and the section list contains
        all the countries that fall in that region.

        :param locale: language of the user.
        :return: formatted list of all destinations.
        :rtype: list
        """
        destinations = Destinations.get_all_destinations(locale=locale)
        all_destinations_list = []
        destinations_list = []
        data = {}
        for destination in destinations:
            region_name = destination.region_name
            section_list = {
                'destination_id': destination.destination_id,
                'position': destination.position,
                'name': destination.name,
                'short_name': destination.shortname,
                'flag_image_url': destination.flag_url,
                'api_params': {
                    'billing_country': destination.shortname,
                    'search_type': 'country'
                }
            }
            if data:
                if region_name in data.get('section_title'):
                    destinations_list.append(section_list)
                else:
                    all_destinations_list.append(data)
                    destinations_list = [section_list]
            else:
                destinations_list = [section_list]
            data = {'section_title': destination.region_name, 'section_list': destinations_list}
        all_destinations_list.append(data)

        return all_destinations_list
