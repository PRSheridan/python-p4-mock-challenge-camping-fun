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
# to_dict serialization rules plugged into a for loop

        campers = [camper.to_dict(rules=('-signups',))
                    for camper in Camper.query.all()]

        return make_response(campers, 200)

    def post(self):
        #get data and split it into bits

        data = request.get_json()
        name = data['name']
        age = data['age']

#try to create new Model, add, and commit
        try:
            camper = Camper(
                name = name,
                age = age,
            )

            db.session.add(camper)
            db.session.commit()

            return camper.to_dict(), 201
#or error
        except ValueError:
            return { "errors": ["validation errors"] }, 400

api.add_resource(Campers, "/campers")


class CampersById(Resource):

    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).one_or_none()

        if camper is None:
            return make_response({'error': 'Camper not found'}, 404)

        return make_response(camper.to_dict(), 200)

    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
#get data and split into bits just like get

        data = request.get_json()
        name = data['name']
        age = data['age']

        if camper is None:
            return make_response({'error': 'Camper not found'}, 404)

        try:
#no add/commit because the camper already exists

            camper.name = name
            camper.age = age
            return camper.to_dict(), 202

        except ValueError:
            return {'errors': ["validation errors"]}, 400

api.add_resource(CampersById, "/campers/<int:id>")


class Activities(Resource):
    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all()]

        return make_response(activities, 200)

api.add_resource(Activities, "/activities")

class ActivitiesById(Resource):
    def delete(self, id):
#look into difference of filter/filter_by
        activity = Activity.query.filter_by(id = id).first()
# if the activity exists, delete, commit 
        if activity:
            db.session.delete(activity)
            db.session.commit()

            return make_response({}, 204)
        return make_response({"error": "Activity not found"}, 404)

api.add_resource(ActivitiesById, "/activities/<int:id>")


class Signups(Resource):
    def post(self):
        data = request.get_json()
        camper_id = data['camper_id']
        activity_id = data['activity_id']
        time = data['time']

        try:
            signup = Signup(
                camper_id = camper_id,
                activity_id = activity_id,
                time = time,
            )

            db.session.add(signup)
            db.session.commit()

            return make_response(signup.to_dict(), 201)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
