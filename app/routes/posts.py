from time import time
from uuid import uuid4
from flask import Blueprint, request, jsonify
from py2neo import Node
from app import graph, repo
from app.models import Post, User, Comment

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


@posts_bp.route("", methods=["GET"])
def get_posts():
    query = "MATCH (p:Post) RETURN p"
    result = graph.run(query)
    posts = []
    for record in result:
        post_node = record["p"]
        posts.append(
            {
                "post_id": post_node.get("post_id"),
                "title": post_node.get("title"),
                "content": post_node.get("content"),
                "created_at": post_node.get("created_at"),
            }
        )
    return jsonify(posts), 200


@posts_bp.route("/<string:post_id>", methods=["GET"])
def get_post_by_id(post_id):
    post = repo.match(Post, post_id).first()

    if post is None:
        return jsonify({"error": "Post not found."}), 404

    post_data = {
        "post_id": post.post_id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
    }

    return jsonify(post_data), 200


@posts_bp.route("/<string:post_id>", methods=["PUT"])
def update_post(post_id):
    data = request.json
    post = repo.match(Post, post_id).first()

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    if "title" in data:
        post.title = data["title"]

    if "content" in data:
        post.content = data["content"]

    repo.save(post)
    return jsonify({"message": "Post succesfully updated"}), 201


@posts_bp.route("/<string:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = repo.match(Post, post_id).first()

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    for comment in post.has_comment:
        repo.delete(comment)
    repo.delete(post)
    return jsonify(), 204


@posts_bp.route("/<string:post_id>/like", methods=["POST"])
def add_like(post_id):
    data = request.json
    if "user_id" not in data:
        return jsonify({"error": "user_id property is missing"}), 400

    user = repo.match(User, data["user_id"]).first()
    if user is None:
        return jsonify({"error": "User not found."}), 404

    post = repo.match(Post, post_id).first()
    if post is None:
        return jsonify({"error": "Post not found."}), 404

    user.posts_likes.add(post)
    repo.save(user)
    return jsonify({"message": f"Post succesfully liked by User {user.user_id}"}), 201


@posts_bp.route("/<string:post_id>/like", methods=["DELETE"])
def remove_like(post_id):
    data = request.json
    if "user_id" not in data:
        return jsonify({"error": "user_id property is missing"}), 400

    user = repo.match(User, data["user_id"]).first()
    if user is None:
        return jsonify({"error": "User not found."}), 404

    post = repo.match(Post, post_id).first()
    if post is None:
        return jsonify({"error": "Post not found."}), 404

    user.posts_likes.remove(post)
    repo.save(user)
    return jsonify({"message": f"Post succesfully unliked by User {user.user_id}"}), 201


@posts_bp.route("/<string:post_id>/comments", methods=["GET"])
def get_post_comments(post_id):
    post = repo.match(Post, post_id).first()
    if post is None:
        return jsonify({"error": "Post not found."}), 404

    post_comments = []
    for comment in post.has_comment:
        post_comments.append(
            {
                "comment_id": comment.comment_id,
                "content": comment.content,
                "created_at": comment.created_at,
            }
        )
    return jsonify(post_comments), 200


@posts_bp.route("/<string:post_id>/comments", methods=["POST"])
def create_comment(post_id):
    data = request.json
    if not "user_id" in data:
        return jsonify({"message": "user_id property is missing"}), 400

    user = repo.match(User, data["user_id"]).first()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    if not "content" in data:
        return jsonify({"message": "content property is missing"}), 400

    post = repo.match(Post, post_id).first()
    if post is None:
        return jsonify({"error": "Post not found."}), 404

    comment = Node(
        "Comment",
        comment_id=str(uuid4()),
        content=data["content"],
        created_at=time(),
    )
    graph.create(comment)

    user.comments_created.add(Comment.wrap(comment))
    post.has_comment.add(Comment.wrap(comment))
    repo.save(user, post)

    return jsonify({"message": "Comment succesfully created"}), 201


@posts_bp.route("/<string:post_id>/comments/<string:comment_id>", methods=["DELETE"])
def delete_post_comment(post_id, comment_id):
    post = repo.match(Post, post_id).first()
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    comment = repo.match(Comment, comment_id).first()
    if comment is None:
        return jsonify({"error": "Comment not found"}), 404

    if comment not in post.has_comment:
        return jsonify({"error": f"Comment not found in Post {post_id}"}), 404

    repo.delete(comment)
    return jsonify(), 204
