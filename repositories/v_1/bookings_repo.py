"""
Bookings Repo module contains all the bookings specific implementation and helper methods.
"""
import base64
import collections
import datetime

from flask import current_app
from werkzeug.exceptions import Forbidden, UnprocessableEntity

from common.constants.colors import Colors
from common.constants.values import StarCategories, URLs
from models.customer_order import CustomerOrder
from models.hb_order import HbOrder
from models.hb_order_status import HbOrderStatus


class BookingsRepo(object):

    MY_BOOKINGS_SCREEN_TITLE = 'My Bookings'
    NO_BOOKINGS_TITLE = "Hotel bookings not found"
    NO_BOOKINGS_SUBTITLE = "You don’t have any hotel bookings history.\n Explore now and start booking!"

    SUCCESS_MESSAGE = "Thank you!" \
                      "Your booking inquiry {bk_num} has been submitted. The hotel will be in touch with you shortly."

    SUCCESS_TITLE = "Inquiry Submitted"

    BOOKING_ERROR_MSG = 'Something went wrong while booking your request.'
    INVALID_DATES_MSG = 'The dates you provided are invalid. Please select correct dates.'

    BOOK_AGAIN_LABEL = 'Book Again'
    BOOKING_DETAILS_LABEL = 'Booking Details'

    MAX_ROOM_CHILD_COUNT = 2
    MAX_ROOM_ADULT_COUNT = 2
    MAX_ROOM_CHILD_AGE = 17

    @classmethod
    def get_hww_bookings(cls, customer_id, locale):

        hww_previous_bookings, hww_upcoming_bookings = [], []
        hww_module_id = current_app.config.get('HWW_MODULE_ID')

        all_bookings = CustomerOrder.get_customer_hotel_bookings(customer_id, locale, hww_module_id)
        for booking in all_bookings:
            check_in_date = booking.checkin_date
            check_out_date = booking.checkout_date
            if check_in_date and check_out_date:
                current_date = datetime.datetime.utcnow().date()
                is_previous_booking = (check_out_date + datetime.timedelta(days=1)) <= current_date

                booking_info = {
                    "sort_date": check_in_date,
                    "lat": booking.lat,
                    "lng": booking.lng,
                    "img_url": booking.photo_retina_url,
                    "order_currency": booking.order_currency,
                    "order_number": booking.order_number,
                    "mobile_phone": booking.telephone,
                    "image_URL": booking.photo_retina_url,
                    "order_id": booking.id,
                    "hotel_id": booking.outlet_id,
                    "banner_label": booking.order_status.title(),
                    "rooms": {
                        "number_of_rooms": booking.number_of_rooms,
                        "room_type": booking.room_type
                    },
                    "hotel_deep_link": URLs.BOOKING_HOTEL_DETAILS_DEEP_LINK.format(
                        merchant_id=booking.merchant_id,
                        outlet_id=booking.outlet_id
                    ),
                    "name": '',
                    "sub_title": '',
                    "star_rating": '',
                    "show_book_again_button": False,
                    "user_booking_web_view_url": '',
                    "is_cancelled": False,
                    "show_booking_banner": True,
                    "banner_color": ''
                }
                sub_title = ", ".join(filter(None, [booking.city_name, booking.country_name]))
                booking_info['sub_title'] = sub_title

                if booking.order_status in (CustomerOrder.ORDER_CANCELLED, CustomerOrder.ORDER_REFUNDED):
                    booking_info.update({
                        "is_cancelled": True,
                        "banner_color": Colors.BRIGHT_RED,
                    })
                elif booking.order_status == CustomerOrder.ORDER_CONFIRMED:
                    if is_previous_booking:
                        booking_info['banner_label'] = CustomerOrder.ORDER_COMPLETED.title()
                    booking_info['banner_color'] = Colors.GREEN

                if booking.hotel:
                    booking_info['name'] = booking.hotel
                elif booking.outlet_name:
                    hotel_name = booking.outlet_name
                    if '-' in hotel_name:
                        hotel_name = hotel_name.split('-')[0].strip()
                    booking_info['name'] = hotel_name

                if booking.sub_categories:
                    sub_categories = [
                        category for category in booking.sub_categories.split(',')
                        if category in StarCategories.VALID_CATEGORIES
                    ]
                    if sub_categories:
                        booking_info['star_rating'] = sub_categories[0]

                if booking.order_number and booking.platform:
                    b64_order_number = base64.b64encode(bytes(booking.order_number, 'utf-8')).decode("utf-8")
                    b64_platform = base64.b64encode(bytes(booking.platform, 'utf-8')).decode("utf-8")
                    if booking_info['is_cancelled']:
                        booking_info['user_booking_web_view_url'] = (
                            current_app.config.get('BOOKING_CANCEL_URL').format(
                                order_number=b64_order_number,
                                platform=b64_platform
                            )
                        )
                    else:
                        booking_info['user_booking_web_view_url'] = (
                            current_app.config.get('BOOKING_SUCCESS_URL').format(
                                order_number=b64_order_number,
                                platform=b64_platform
                            )
                        )

                # Date information update.
                booking_info.update({
                    "check_in_date": check_in_date.strftime("%d-%m-%Y"),
                    "check_in_text": check_in_date.strftime("%b %d, %a"),
                    "check_in_date_label": check_in_date.strftime("%b %d"),
                    "check_in_day_label": check_in_date.strftime("%A"),
                    "month_title_label": check_in_date.strftime("%b"),
                    "check_out_date": check_out_date.strftime("%d-%m-%Y"),
                    "check_out_text": check_out_date.strftime("%b %d, %a"),
                    "check_out_date_label": check_out_date.strftime("%b %d"),
                    "check_out_day_label": check_out_date.strftime("%A")
                })

                # Colors and static texts update.
                booking_info.update({
                    "check_in_label_color": Colors.LIGHT_GREY,
                    "check_in_date_label_color": Colors.DARK_GREY,
                    "check_in_text_color": Colors.DARK_GREY,
                    "check_in_day_label_color": Colors.DARK_GREY,
                    "check_in_label": "Check-in: ",
                    "check_out_label_color": Colors.LIGHT_GREY,
                    "check_out_date_label_color": Colors.DARK_GREY,
                    "check_out_text_color": Colors.DARK_GREY,
                    "check_out_day_label_color": Colors.DARK_GREY,
                    "check_out_label": "Check-out: ",
                    "sub_title_color": Colors.DARK_GREY

                })
                if is_previous_booking:
                    booking_info["show_book_again_button"] = True
                    booking_info['action_label'] = cls.BOOK_AGAIN_LABEL
                    hww_previous_bookings.append(booking_info)
                else:
                    booking_info['action_label'] = cls.BOOKING_DETAILS_LABEL
                    hww_upcoming_bookings.append(booking_info)

        return hww_previous_bookings, hww_upcoming_bookings

    @classmethod
    def get_getaways_bookings(cls, customer_id):

        gtwys_previous_bookings, gtwys_upcoming_bookings = [], []

        all_bookings = HbOrder.get_customer_getaways_bookings(customer_id=customer_id)
        for booking in all_bookings:
            check_in_date = booking.checkin_date
            check_out_date = booking.checkout_date
            if check_in_date and check_out_date:
                current_date = datetime.datetime.utcnow().date()
                is_previous_booking = (check_out_date + datetime.timedelta(days=1)) <= current_date

                booking_info = {
                    "sort_date": check_in_date,
                    "lat": booking.lat,
                    "lng": booking.lng,
                    "img_url": booking.photo_retina_url,
                    "order_currency": booking.order_currency,
                    "order_number": booking.order_number,
                    "mobile_phone": booking.telephone,
                    "image_URL": booking.photo_retina_url,
                    "order_id": booking.id,
                    "hotel_id": booking.hotel_id,
                    "banner_label": booking.order_status_label,
                    "star_rating": booking.star_rating,
                    "rooms": {
                        "number_of_rooms": booking.number_of_rooms,
                        "room_type": booking.room_type
                    },
                    "name": booking.hotel_name,
                    "sub_title": '',
                    "show_book_again_button": False,
                    "user_booking_web_view_url": '',
                    "is_cancelled": False,
                    "show_booking_banner": True,
                    "banner_color": ''
                }
                sub_title = ", ".join(filter(None, [booking.city_name, booking.country_name]))
                booking_info['sub_title'] = sub_title

                if booking.is_cancelled and booking.order_status == HbOrderStatus.CANCELLED:
                    booking_info.update({
                        "is_cancelled": True,
                        "banner_color": Colors.BRIGHT_RED,
                    })
                elif booking.order_status == HbOrderStatus.CONFIRMED:
                    if is_previous_booking:
                        booking_info['banner_label'] = 'Completed'
                    booking_info['banner_color'] = Colors.GREEN

                # Date information update.
                booking_info.update({
                    "check_in_date": check_in_date.strftime("%d-%m-%Y"),
                    "check_in_text": check_in_date.strftime("%b %d, %a"),
                    "check_in_date_label": check_in_date.strftime("%b %d"),
                    "check_in_day_label": check_in_date.strftime("%A"),
                    "month_title_label": check_in_date.strftime("%b"),
                    "check_out_date": check_out_date.strftime("%d-%m-%Y"),
                    "check_out_text": check_out_date.strftime("%b %d, %a"),
                    "check_out_date_label": check_out_date.strftime("%b %d"),
                    "check_out_day_label": check_out_date.strftime("%A")
                })

                # Colors and static texts update.
                booking_info.update({
                    "check_in_label_color": Colors.LIGHT_GREY,
                    "check_in_date_label_color": Colors.DARK_GREY,
                    "check_in_text_color": Colors.DARK_GREY,
                    "check_in_day_label_color": Colors.DARK_GREY,
                    "check_in_label": "Check-in: ",
                    "check_out_label_color": Colors.LIGHT_GREY,
                    "check_out_date_label_color": Colors.DARK_GREY,
                    "check_out_text_color": Colors.DARK_GREY,
                    "check_out_day_label_color": Colors.DARK_GREY,
                    "check_out_label": "Check-out: ",
                    "sub_title_color": Colors.DARK_GREY

                })
                if is_previous_booking:
                    gtwys_previous_bookings.append(booking_info)
                else:
                    gtwys_upcoming_bookings.append(booking_info)

        return gtwys_previous_bookings, gtwys_upcoming_bookings

    def get_user_previous_and_upcoming_bookings(self, customer_id, locale):
        """
        Gets users all booking requests and classifies them in previous/upcoming sections.

        NOTE: Removed order_by from queries since now we are also getting getaways bookings and reordering them.

        :param int customer_id: The id of customer for which we need to get bookings.
        :param str locale: locale of the user.
        :rtype: tuple
        """
        upcoming_bookings = []
        previous_bookings = []

        hww_prev, hww_upcoming = self.get_hww_bookings(customer_id=customer_id, locale=locale)
        if hww_prev:
            previous_bookings.extend(hww_prev)
        if hww_upcoming:
            upcoming_bookings.extend(hww_upcoming)

        gtwys_prev, gtwys_upcoming = self.get_getaways_bookings(customer_id=customer_id)
        if gtwys_prev:
            previous_bookings.extend(gtwys_prev)
        if gtwys_upcoming:
            upcoming_bookings.extend(gtwys_upcoming)

        if previous_bookings:
            previous_bookings = self._sort_bookings(previous_bookings, is_reverse=True)
        if upcoming_bookings:
            upcoming_bookings = self._sort_bookings(upcoming_bookings)

        return upcoming_bookings, previous_bookings

    @staticmethod
    def _sort_bookings(bookings, is_reverse=False):
        """
        Sorts booking based on temporary date field added for sorting and then deletes the date field for
        JSON serialization.
        """
        bookings.sort(key=lambda _: _['sort_date'], reverse=is_reverse)
        for booking in bookings:
            del booking['sort_date']

        return bookings

    @staticmethod
    def validate_cin_cout_dates(check_in_date, check_out_date):
        """
        Validate check-in and check-out dates.
        Conditions:
        > Check-in date must be in the future.
        > Check-out date must be in the future.
        > Check-in date must come before check-out date.

        :param date check_in_date: check in date of the hotel
        :param date check_out_date: check out date of the hotel
        :rtype: Exception, bool.
        """
        if check_in_date < datetime.date.today():
            raise UnprocessableEntity(
                "Don't allowed past dates in check_in_date {check_in_date}".format(check_in_date=str(check_in_date))
            )

        if check_out_date < datetime.date.today():
            raise UnprocessableEntity(
                "Don't allowed past dates in check_out_date {check_out_date}".format(check_out_date=str(check_out_date))
            )

        if check_in_date > check_out_date:
            raise UnprocessableEntity(
                "Check-in date {check_in_date} must be earlier than Check-out {check_out_date}".format(
                    check_in_date=str(check_in_date),
                    check_out_date=str(check_out_date)
                )
            )

        return True

    @classmethod
    def validate_rooms(cls, rooms_params):
        """
        Validates the rooms.
        :param rooms_params: dict of the rooms
        """
        rooms = {}
        mongo_rooms = []
        for room_index, room_info in enumerate(rooms_params):
            try:
                rooms['Room']
            except KeyError:
                rooms['Room'] = []

            try:
                adults_count = int(room_info.get('a', 0))
                if adults_count > cls.MAX_ROOM_ADULT_COUNT:
                    raise Forbidden(
                        "Adult count must be less than {adult_count} for room number {room_number}".format(
                            adult_count=cls.MAX_ROOM_ADULT_COUNT,
                            room_number=room_index + 1
                        )
                    )
            except ValueError:
                raise Forbidden(
                    "Adult count must be integer for room number {room_number}".format(room_number=room_index + 1)
                )

            try:
                children_count = int(room_info.get('c', 0))
                if children_count > cls.MAX_ROOM_CHILD_COUNT:
                    raise Forbidden(
                        "Children count must be less than {children_count} for room number {room_number}".format(
                            children_count=cls.MAX_ROOM_CHILD_COUNT,
                            room_number=room_index + 1
                        )
                    )
            except ValueError:
                raise Forbidden(
                    "Children count must be integer for room number {room_number}".format(room_number=room_index + 1)
                )

            for children_age in room_info.get('c_ages', []):
                try:
                    children_ages = int(children_age)
                    if children_ages > cls.MAX_ROOM_CHILD_AGE:
                        raise Forbidden(
                            "Children age must be less than {children_count} for room number {room_number}".format(
                                children_count=cls.MAX_ROOM_CHILD_AGE,
                                room_number=room_index + 1
                            )
                        )
                except ValueError:
                    raise Forbidden(
                        "Children ages must be integer for room number {room_number}".format(room_number=room_index + 1)
                    )

            single_room = collections.OrderedDict()
            single_room['Adults'] = adults_count
            if room_info.get('c', 0) and room_info.get('c_ages', []):
                single_room['Children'] = room_info.get('c', 0)
                single_room['ChildAge'] = room_info.get('c_ages', [])
            mongo_rooms.append({'Room': single_room})
            rooms['Room'].append(single_room)

        return rooms, mongo_rooms
