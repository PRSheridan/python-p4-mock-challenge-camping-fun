#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(rules=('-signups',))
                    for camper in Camper.query.all()]

        return make_response(campers, 200)

api.add_resource(Campers, "/campers")

class CampersByID(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).one_or_none()

        if camper is None:
            return make_response({'error': 'Camper not found'}, 404)
            
        return make_response(camper.to_dict(), 200)

api.add_resource(CampersByID, "/campers/<int:id>")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
