from flask import Flask,request,Response,Blueprint
from pymongo import MongoClient
import json
import bcrypt
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required, get_jwt_identity, JWTManager
from modules.db import DB

db = DB()
users = db.get_user_collection()


auth_handler = Blueprint('authentication', __name__)

@auth_handler.route('/signup', methods=['POST'])
def user_sign_up():
    request_data = request.get_json()
    user_name = request_data['name']
    user_email = request_data['email']
    user_password = request_data['password']
    email_found = users.find_one({"email": user_email})
    if email_found:
        message = 'There already is a user by that email'
        return Response(json.dumps({'success': False, 'err': message})), 202
    pw_hash = bcrypt.hashpw(user_password.encode('utf8'), bcrypt.gensalt())
    user_input = {'name': user_name, 'email': user_email, 'password': pw_hash}
    userInsert = users.insert_one(user_input)
    access_token = create_access_token(identity=user_email, fresh=True)
    refresh_token = create_refresh_token(identity=user_email)
    return Response(json.dumps({'login': True, 'msg': 'User created', 'success': True,'user':{'name':user_name,'email':user_email}, 'access_token': access_token,'refresh_token':refresh_token})), 200


@auth_handler.route('/login', methods=['POST'])
def user_login():
    try:
        request_data = request.get_json()
        user_email = request_data['email']
        user_password = request_data['password']
        user_data = users.find_one({"email": user_email})
        try:
            user_data
            passwd = bcrypt.checkpw(user_password.encode(
                'utf8'), user_data['password'])
            if (passwd):
                access_token = create_access_token(identity=user_email, fresh=True)
                refresh_token = create_refresh_token(identity=user_email)
                return Response(json.dumps({'login': True, 'msg': 'User Logged in', 'success': True,'user':{'name':user_data['name'],'email':user_data['email']}, 'access_token': access_token, 'refresh_token':refresh_token})), 200
            else:
                return Response(json.dumps({'login': False, 'msg': 'user password incorrect'})), 403
        except:
            return Response(json.dumps({'err': 'Unauthorized access'})), 401
    except:
        return Response(json.dumps({'err': 'Internal server error'})), 500


@auth_handler.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return Response(json.dumps({'access_token':access_token})),200




