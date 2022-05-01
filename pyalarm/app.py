import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Union

from flask import Flask, request, make_response, jsonify
import jwt
from flask_migrate import Migrate
from werkzeug.security import check_password_hash

from models.core import User, Location, UserConfig
from .models import devices
from . import serializers

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.pwd_hash, password):
        return user.id

def identity(payload):
    user_id = payload['identity']
    return User.query.filter_by(id=user_id).first()

# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query \
                .filter_by(id=data['public_id']) \
                .first()
        except jwt.DecodeError:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        return f(current_user, *args, **kwargs)

    return decorated

def get_user_location(user_id, location_id) -> Location:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        user = None
    try:
        location = Location.objects.get(pk=location_id)
    except Location.DoesNotExist:
        location = None
    if user & location in user.locations:
        user_config = UserConfig.objects.get(user=user, location=location)
    if user_config:
        try:
            configured_location = location.configure(user_config.pk)
        except Location.ConfigFailed:
            configured_location = None
    return configured_location

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ('PYALARM_SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ('PYALARM_DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# @token_required - Will eventually make this private.
@app.post('/add_user')
def user_add():
    json_data = request.get_json()
    username: str = json_data['username']
    email: str = json_data['email']
    password: str = json_data['password']
    user = add_user(username=username, email=email, password=password)
    return user


@app.route('/login', methods=['POST'])
def login():
    # creates dictionary of form data
    auth = request.get_json()

    if not auth or not auth['username'] or not auth['password']:
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.query \
        .filter_by(username=auth.get('username')) \
        .first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.pwd_hash, str(auth['password'])):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


@token_required
def location_status(current_user, location_id:int=None):
    if not location_id:
        return {
                   "status": "error"
                   "message": "No location id provided."
               }
    location =  get_user_location(current_user.pk, location_id)
    if location:
        stats = location.get_status(current_user.pk)
    else:
        stats = {
            "error": "No user config found for location."
        }
    response = {"status": "success", "message": stats}
    return response

@token_required
def add_location(current_user, data: dict=None):
    if not data:
        return {
               "status": "error",
               "message": "No location data provided."
               }
    message = "Not implemented yet."
    return {"status": "success", "message": message}
