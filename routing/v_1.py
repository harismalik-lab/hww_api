"""
Routing for HotelWorldWide
"""
from routing.base_routing import BaseRouting
from web_api.hww_apis.v_1.booking_inquiry.api import HwwBookingInquiry
from web_api.hww_apis.v_1.bookings.api import HwwBookings
from web_api.hww_apis.v_1.clear_history.api import HwwClearHistory
from web_api.hww_apis.v_1.config.api import HwwConfig
from web_api.hww_apis.v_1.filters.api import HwwFilters
from web_api.hww_apis.v_1.home.api import HwwHome
from web_api.hww_apis.v_1.hotel_details.api import HwwDetails
from web_api.hww_apis.v_1.hotel_listing.api import HwwHotelListing
from web_api.hww_apis.v_1.redemption.api import HwwRedemption
from web_api.hww_apis.v_1.search.api import HwwSearch


class HwwRouting(BaseRouting):
    api_version = '1'

    def set_routing_collection(self):
        self.routing_collection['home'] = {'view': HwwHome, 'url': '/home'}
        self.routing_collection['hotel-details'] = {'view': HwwDetails, 'url': '/hotel_details'}
        self.routing_collection['listing'] = {'view': HwwHotelListing, 'url': '/hotels_listing'}
        self.routing_collection['search'] = {'view': HwwSearch, 'url': '/search'}
        self.routing_collection['filters'] = {'view': HwwFilters, 'url': '/filters'}
        self.routing_collection['bookings'] = {'view': HwwBookings, 'url': '/bookings'}
        self.routing_collection['redemptions'] = {'view': HwwRedemption, 'url': '/redemptions'}
        self.routing_collection['config'] = {'view': HwwConfig, 'url': '/config'}
        self.routing_collection['booking_inquiry'] = {'view': HwwBookingInquiry, 'url': '/booking_inquiry'}
        self.routing_collection['clear_history'] = {'view': HwwClearHistory, 'url': '/clear_history'}
