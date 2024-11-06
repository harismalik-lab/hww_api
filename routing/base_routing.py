"""
Base routing file. Includes all the routing information and mapping of urls
"""
from flask import Blueprint
from flask_restful import Api

from app_configurations.settings import API_PREFIX
from web_api.hww_apis.v_1.health_check.api import HealthCheckAPI


class BaseRouting(object):
    api = None
    api_bp = None
    app = None
    api_version = ''
    base_url = API_PREFIX
    routing_collection = {}
    health_check_path = '/healthcheck'
    health_check_api_name = 'health-check'

    def __init__(self, app=None, name='__main__'):
        self.app = app
        blue_print_version = 'api_v{api_version}'.format(
            api_version=self.api_version,
        )
        self.api_bp = Blueprint(blue_print_version, name)

        self.api = Api(self.api_bp)

    def set_routing_collection(self):
        pass

    def update_routing_collection(self):
        pass

    def add_resources(self):
        if self.api_version == '1':  # To add it once for initial version
            self.api.add_resource(
                HealthCheckAPI,
                self.health_check_path,
                endpoint=self.health_check_api_name
            )
        for api_name, api_info in self.routing_collection.items():
            self.api.add_resource(
                api_info.get('view'),
                api_info.get('url'),
                endpoint=api_name
            )
        self.app.register_blueprint(
            self.api_bp,
            url_prefix="/{base_url}/v{api_version}".format(
                base_url=self.base_url,
                api_version=self.api_version
            )
        )

    def map_urls(self):
        self.set_routing_collection()
        self.update_routing_collection()
        self.add_resources()
