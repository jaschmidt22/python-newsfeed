from flask import Blueprint, request, jsonify, session
from app.models import User, Post, Comment, Vote
from app.db import get_db
import sys
from app.utils.auth import login_required

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

@bp.route('/comments', methods=['POST'])
@login_required
def comment():
    data = request.get_json()
    db = get_db()

    try:
        # create a new comment
        newComment = Comment(
            comment_text=data['comment_text'],
            post_id=data['post_id'],
            user_id=session.get('user_id')
        )

        db.add(newComment)
        db.commit()
        return jsonify(id=newComment.id), 201

    except Exception as e:
        print(sys.exc_info()[0], e)
        db.rollback()
        return jsonify(message='Comment failed'), 500

@bp.route('/posts/upvote', methods=['PUT'])
@login_required
def upvote():
    data = request.get_json()
    db = get_db()

    try:
        # create a new vote with incoming id and session id
        newVote = Vote(
            post_id=data['post_id'],
            user_id=session.get('user_id')
        )

        db.add(newVote)
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message = 'Upvote failed'), 500
        
    return '', 204

@bp.route('/posts', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    db = get_db()

    try:
    # create a new post
        newPost = Post(
            title = data['title'],
            post_url = data['post_url'],
            user_id = session.get('user_id')
    )

        db.add(newPost)
        db.commit()
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Post failed'), 500

    return jsonify(id = newPost.id)

@bp.route('/posts/<id>', methods=['PUT'])
@login_required
def update(id):
    data = request.get_json()
    db = get_db()

    try:
        # retrieve post and update title
        post = db.query(Post).filter(Post.id == id).one()
        post.title = data['title']
        db.commit()
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Post update failed'), 500

    return '', 204

@bp.route('/posts/<id>', methods=['DELETE'])
@login_required
def delete(id):
    db = get_db()

    try:
    # delete post from db
        db.delete(db.query(Post).filter(Post.id == id).one())
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message = 'Post not found'), 404
    
    return '', 204