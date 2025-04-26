from time import time
from uuid import uuid4
from flask import Blueprint, request, jsonify
from py2neo import Node
from app import graph, repo
from app.models import User, Post

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
def get_users():
    """
    Get all users
    ---
    tags:
      - Users
    responses:
      200:
        description: A list of users
        schema:
          type: array
          items:
            type: object
            properties:
              user_id:
                type: string
                description: The user's ID (uuid)
              name:
                type: string
                description: The user's name
              email:
                type: string
                description: The user's email address
              created_at:
                type: string
                description: The date the user was created
        examples:
            application/json: [
                {
                    "user_id": "fb8f24eb-01a9-4f49-b324-e34106c9f73c",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "created_at": "1745676650"
                }
            ]
    """
    query = "MATCH (u:User) RETURN u"
    result = graph.run(query)
    users = []
    for record in result:
        user_node = record["u"]
        users.append(
            {
                "user_id": user_node.get("user_id"),
                "name": user_node.get("name"),
                "email": user_node.get("email"),
                "created_at": user_node.get("created_at"),
            }
        )
    return jsonify(users), 200


@users_bp.route("/<string:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    """
    Get a user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: A user
        examples:
            application/json: {
                "user_id": "fb8f24eb-01a9-4f49-b324-e34106c9f73c",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "created_at": "1745676650"
            }
      404:
        description: User not found
    """

    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    user_data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at,
    }

    return jsonify(user_data), 200


@users_bp.route("", methods=["POST"])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
    responses:
      201:
        description: User succesfully created
      400:
        description: Missing name or email fields
    """

    data = request.json

    if not "name" in data:
        return jsonify({"message": "name property is missing"}), 400

    if not "email" in data:
        return jsonify({"message": "email property is missing"}), 400

    user = Node(
        "User",
        user_id=str(uuid4()),
        name=data["name"],
        email=data["email"],
        created_at=time(),
    )
    graph.create(user)
    return jsonify({"message": "User succesfully created"}), 201


@users_bp.route("/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Update an existing user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
    responses:
      201:
        description: User succesfully updated
      404:
        description: User not found
    """

    data = request.json
    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        user.email = data["email"]

    repo.save(user)
    return jsonify({"message": "User succesfully updated"}), 201


@users_bp.route("/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      204:
        description: User succesfully deleted
      404:
        description: User not found
    """

    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    repo.delete(user)
    return jsonify(), 204


@users_bp.route("/<string:user_id>/friends", methods=["GET"])
def get_user_friends(user_id):
    """
    Get a user's friends
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: A list of user's friends
      404:
        description: User not found
    """

    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    user_friends = []
    for friend in user.friends_with:
        user_friends.append({"user_id": friend.user_id, "name": friend.name})

    user_data = {
        "user_id": user.user_id,
        "friends": user_friends,
    }

    return jsonify(user_data), 200


@users_bp.route("/<string:user_id>/friends", methods=["POST"])
def add_friend_to_user(user_id):
    """
    Add a friend to a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            friend_id:
              type: string
    responses:
      201:
        description: Friend succesfully added
      400:
        description: Missing friend_id field
      404:
        description: User or friend not found
    """

    data = request.json
    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    if "friend_id" not in data:
        return jsonify({"error": "friend_id property is missing"}), 400

    new_friend = repo.match(User, data["friend_id"]).first()

    if new_friend is None:
        return jsonify({"error": "Friend User to add not found."}), 404

    user.friends_with.add(new_friend)
    new_friend.friends_with.add(user)
    repo.save(user, new_friend)
    return jsonify({"message": "Friend succesfully added"}), 201


@users_bp.route("/<string:user_id>/friends/<string:friend_id>", methods=["DELETE"])
def remove_friend_to_user(user_id, friend_id):
    """
    Remove a friend from a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - name: friend_id
        in: path
        type: string
        required: true
    responses:
      201:
        description: Friend succesfully removed
      404:
        description: User or friend not found
    """

    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    friend = repo.match(User, friend_id).first()

    if friend is None:
        return jsonify({"error": "Friend User to remove not found."}), 404

    user.friends_with.remove(friend)
    friend.friends_with.remove(user)
    repo.save(user, friend)
    return jsonify({"message": "Friend succesfully removed"}), 201


@users_bp.route("/<string:user_id>/friends/<string:friend_id>", methods=["GET"])
def check_users_are_friends(user_id, friend_id):
    """
    Check if two users are friends
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - name: friend_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: True if users are friends, False otherwise
      404:
        description: User or friend not found
    """

    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    friend = repo.match(User, friend_id).first()

    if friend is None:
        return jsonify({"error": "Friend User not found."}), 404

    if friend in user.friends_with:
        return jsonify(True), 200
    return jsonify(False), 200


@users_bp.route("/<string:user_id>/mutual-friends/<string:other_id>", methods=["GET"])
def get_mutual_friends(user_id, other_id):
    """
    Get mutual friends between two users
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - name: other_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: A list of mutual friends
      404:
        description: User or other user not found
    """

    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    other_user = repo.match(User, other_id).first()

    if other_user is None:
        return jsonify({"error": "Other User not found."}), 404

    user_friends = []
    for friend in user.friends_with:
        user_friends.append(friend.user_id)

    other_user_friends = []
    for friend in other_user.friends_with:
        other_user_friends.append(friend.user_id)

    mutual_friends = list(frozenset(user_friends).intersection(other_user_friends))

    return jsonify(mutual_friends), 200


@users_bp.route("/<string:user_id>/posts", methods=["GET"])
def get_user_posts(user_id):
    """
    Get posts created by a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: A list of user's posts
      404:
        description: User not found
    """

    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    user_posts = []
    for post in user.created:
        user_posts.append(
            {
                "post_id": post.post_id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at,
            }
        )
    return jsonify(user_posts), 200


@users_bp.route("/<string:user_id>/posts", methods=["POST"])
def create_post(user_id):
    """
    Create a post for a user
    ---
    tags:
      - Posts
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            content:
              type: string
    responses:
      201:
        description: Post created
      400:
        description: Missing title or content fields
      404:
        description: User not found
    """

    data = request.json
    user = repo.match(User, user_id).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    if not "title" in data:
        return jsonify({"message": "title property is missing"}), 400

    if not "content" in data:
        return jsonify({"message": "content property is missing"}), 400

    post = Node(
        "Post",
        post_id=str(uuid4()),
        title=data["title"],
        content=data["content"],
        created_at=time(),
    )
    graph.create(post)

    user.posts_created.add(Post.wrap(post))
    repo.save(user)
    return jsonify({"message": "Post succesfully created"}), 201
