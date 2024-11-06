"""
Health Check API
"""
from flask import current_app
from flask_restful import Resource
from requests import codes

from models.db import db


class HealthCheckAPI(Resource):

    def get(self):
        if current_app.config['ALIVE']:
            try:
                db.session.execute("SELECT 1;")
            except Exception:
                return "SQL connectivity issue", codes.UNPROCESSABLE_ENTITY
            return "I am alive.", codes.OK
        else:
            return "I am dead.", codes.UNPROCESSABLE_ENTITY
