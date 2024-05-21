from flask import Blueprint, request, jsonify, session
from app.models import User
from app.db import get_db
import sys

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/users', methods=['POST'])
def signup():
    data = request.get_json()
    db = get_db()

    try:
        # Attempt creating a new user
        newUser = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )

        db.add(newUser)
        db.commit()

        # Set session variables for the new user
        session['user_id'] = newUser.id
        session['loggedIn'] = True

        return jsonify(message='Signup successful'), 201

    except Exception as e:
        # Print the exception for debugging
        print(sys.exc_info()[0], e)

        # Rollback the session in case of an error
        db.rollback()
        
        # Clear the session in case of failure
        session.clear()

        return jsonify(message='Signup failed'), 500

@bp.route('/users/logout', methods=['POST'])
def logout():
    # Remove session variables
    session.clear()
    return '', 204

@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()

    try:
        user = db.query(User).filter(User.email == data['email']).one()
    except Exception as e:
        # Print the exception for debugging
        print(sys.exc_info()[0], e)
        return jsonify(message='Incorrect credentials'), 400

    if not user.verify_password(data['password']):
        return jsonify(message='Incorrect credentials'), 400

    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True

    return jsonify(id=user.id)
