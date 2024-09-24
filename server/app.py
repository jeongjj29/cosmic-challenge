#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from werkzeug.exceptions import NotFound
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

api = Api(app)

db.init_app(app)

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        scientists_dict = [scientist.to_dict(rules=("-missions", "-planets")) for scientist in scientists]
        return make_response(scientists_dict, 200)
    
    def post(self):
        data = request.get_json()
        try:
            scientist = Scientist(**data)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
        db.session.add(scientist)
        db.session.commit()
        return make_response(scientist.to_dict(), 201)


class ScientistsById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).one_or_none()
        if not scientist:
            raise NotFound
        scientist_dict = scientist.to_dict()
        return make_response(scientist_dict, 200)
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).one_or_none()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        data = request.get_json()
        try:
            for key, value in data.items():
                setattr(scientist, key, value)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
        db.session.add(scientist)
        db.session.commit()
        return make_response(scientist.to_dict(), 202)
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).one_or_none()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)
    
class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        planets_dict = [planet.to_dict(rules=("-missions", "-scientists")) for planet in planets]
        return make_response(planets_dict, 200)

class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            mission = Mission(**data)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
        db.session.add(mission)
        db.session.commit()
        return make_response(mission.to_dict(), 201)

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

@app.errorhandler(NotFound)
def handle_404(exception):
    path = request.path
    cleaned_path = "".join(char for char in path if char.isalpha())
    response = make_response( {"error": f"{cleaned_path.title()} not found" }, 404)
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
