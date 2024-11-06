"""
Search Repo module contains all the search specific implementation and helper methods.
"""
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from flask import current_app

from common.constants.icons import Icons
from common.constants.strings import CommonStrings
from common.constants.values import CommonValues
from models.mongo_models.searches import Searches


class SearchRepo(object):
    SEARCH_NO_RESULTS = 'No results found for "{query}". Please try changing your search criteria.'
    SECTION_POPULAR_DESTINATIONS_TITLE = 'POPULAR DESTINATIONS'
    SECTION_RECENT_SEARCHES_TITLE = 'RECENT SEARCHES'
    EMPTY_SECTION_TITLE = "Uh Oh!"
    SEARCH_TYPE_CITY = 'city'
    SEARCH_TYPE_COUNTRY = 'country'
    SEARCH_TYPE_HOTEL = 'hotel'

    def __init__(self):
        self.es = Elasticsearch([current_app.config.get("ELASTIC_SEARCH_BASE_URL")])

    @staticmethod
    def get_auto_suggest_es_query(query_string, lat, lng, fuzziness):
        """
        Formulates and returns the elastic search query for travel outlets.

        This function uses bool query to match multiple fields present in the et_travel. Destinations are preferred
        over outlets hence a boosting query.

        :param str query_string: text query passed to find matches in indexed data.
        :param float lat: latitude of user.
        :param float lng: longitude of user.
        :param (int, 'AUTO') fuzziness: maximum allowed Levenshtien edit distance or 'AUTO' which puts this
                                        responsibility on ElasticSearch.
        :return: query body for the passed index.
        :rtype: dict
        """
        query_body = dict()
        query_dict = {
            "function_score": {
                "query": {
                    "boosting": {
                        "positive": {
                            "multi_match": {
                                "query": query_string,
                                "fields": ["name^2", "address"],
                                "operator": "and",
                                "fuzziness": fuzziness
                            }
                        },
                        "negative": {
                            "bool": {
                                "should": {
                                    "term": {
                                        "type": "hotel"
                                    }
                                }
                            }
                        },
                        "negative_boost": 0.9
                    }
                },

                "functions": [
                    {
                        "filter": {
                            "term": {
                                "type": "hotel"
                            }
                        },

                        "gauss": {
                            "geo_location": {
                                "origin": {
                                    "lat": lat,
                                    "lon": lng
                                },
                                "scale": "10km",
                            }
                        }
                    }
                ]
            },
        }

        query_body["query"] = query_dict
        return query_body

    def get_auto_complete_results(self, query, lat, lng):
        """
        Gets auto complete results for Travel search bar.

        This function hits et_travel ES index to get autocomplete results for passed query string and then gets data.
        We get both non-fuzzy and fuzzy results and prioritize non-fuzzy i.e. exact match results over fuzzy results.

        :param str query: text query passed to find matches in indexed data.
        :param float lat: latitude of user.
        :param float lng: longitude of user.
        :return: a formatted list of all hits got from ElasticSearch.
        :rtype: list
        """

        auto_complete_response = []
        if not query:
            return auto_complete_response

        search_body = []
        for fuzziness_level in ["0", "AUTO"]:
            search_body.append({"index": CommonValues.ES_TRAVEL_INDEX})
            query_body = self.get_auto_suggest_es_query(query, lat, lng, fuzziness_level)
            search_body.append(query_body)
        try:
            auto_complete_results = self.es.msearch(body=search_body)
        except ESConnectionError:
            auto_complete_results = {}

        responses = auto_complete_results.get('responses', [])
        try:
            non_fuzzy_results = responses[0].get(CommonStrings.HITS, {}).get(CommonStrings.HITS, [])
        except IndexError:
            non_fuzzy_results = []
        try:
            fuzzy_results = responses[1].get(CommonStrings.HITS, {}).get(CommonStrings.HITS, [])
        except IndexError:
            fuzzy_results = []

        results = non_fuzzy_results or fuzzy_results

        if results:
            for option in results:
                document = option.get('_source', {})
                doc_type = document.get('type', '')
                icon_image = Icons.LOCATION_PIN
                if doc_type == 'hotel':
                    icon_image = Icons.HOTEL_PIN
                title = document.get('name', '')
                if len(title) > 40:
                    title = '{title}...'.format(title=title[:40])
                full_title = document.get('name', '')
                city = document.get('city', '')
                country = document.get('country', '')
                sub_title = document.get('address', '')
                search_result_object = {
                    'title': title,
                    'full_title': full_title,
                    'sub_title': sub_title,
                    'latitude': document.get('lat', 0.0),
                    'longitude': document.get('lng', 0.0),
                    'icon_image': icon_image,
                    'type': doc_type,
                    'is_hww_instant_booking': document.get('is_hww_instant_booking')
                }
                search_params = {
                    'query': full_title,
                    'map_lat': document.get('lat'),
                    'map_lng': document.get('lng'),
                }
                if doc_type == self.SEARCH_TYPE_CITY:
                    search_params.update({
                        'search_type': self.SEARCH_TYPE_CITY,
                        'billing_city': city
                    })
                elif doc_type == self.SEARCH_TYPE_COUNTRY:
                    search_params.update({
                        'search_type': self.SEARCH_TYPE_COUNTRY,
                        'billing_country': country
                    })
                else:
                    search_params.update({
                        'search_type': self.SEARCH_TYPE_HOTEL,
                        'outlet_id': document.get('outlet_id'),
                        'merchant_id': document.get('merchant_id'),
                        'is_hww_instant_booking': document.get('is_hww_instant_booking')
                    })
                search_result_object['api_params'] = search_params
                auto_complete_response.append(search_result_object)

        return auto_complete_response

    def get_user_recent_searches(self, customer_id):
        """
        Helper function around MONGO's response to get recent searches of a user.

        :param int customer_id: the id of customer.
        :return: list of user's searches.
        :rtype: list
        """
        user_recent_searches = []
        recent_searches = Searches.get_recent_searches(customer_id=customer_id)
        for search_item in recent_searches:
            doc_title = search_item.title
            doc_type = search_item.search_type
            search_obj = {
                'title': search_item.title,
                'type': doc_type,
                'api_params': {
                    'query': doc_title,
                    'search_type': doc_type
                }
            }
            if doc_type == self.SEARCH_TYPE_CITY:
                search_obj['api_params']['billing_city'] = search_item.city
            elif doc_type == self.SEARCH_TYPE_COUNTRY:
                search_obj['api_params']['billing_country'] = search_item.country
            else:
                search_obj['api_params'].update({
                    'outlet_id': search_item.outlet_id,
                    'merchant_id': search_item.merchant_id,
                })
            user_recent_searches.append(search_obj)

        return user_recent_searches

    @classmethod
    def get_popular_destinations(cls, locale):
        """
        Gets the popular destinations for the desired locale.
        :rtype: list[dict]
        """

        from models.destinations import Destinations

        popular_destinations_list = []
        popular_destinations = Destinations.get_popular_destinations(locale)

        for destination in popular_destinations:
            destination_obj = {
                'title': destination.title,
                'destination_id': destination.id,
                'api_params': {
                    "search_type": destination.type,
                }
            }
            if destination.type == cls.SEARCH_TYPE_CITY:
                destination_obj['api_params']['billing_city'] = destination.billing_city

            if destination.type == cls.SEARCH_TYPE_COUNTRY:
                destination_obj['api_params']['billing_country'] = destination.billing_country

            popular_destinations_list.append(destination_obj)

        return popular_destinations_list
