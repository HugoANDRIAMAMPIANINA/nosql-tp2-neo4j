from flask import Blueprint, request, jsonify
from py2neo import Node
from app import graph, repo
from app.models import Post, User, Comment

comments_bp = Blueprint("comments", __name__, url_prefix="/comments")


@comments_bp.route("", methods=["GET"])
def get_comments():
    query = "MATCH (c:Comment) RETURN c"
    result = graph.run(query)
    comments = []
    for record in result:
        comment_node = record["c"]
        comments.append(
            {
                "comment_id": comment_node.get("comment_id"),
                "content": comment_node.get("content"),
                "created_at": comment_node.get("created_at"),
            }
        )
    return jsonify(comments), 200


@comments_bp.route("/<string:comment_id>", methods=["GET"])
def get_comment_by_id(comment_id):
    comment = repo.match(Comment, comment_id).first()

    if comment is None:
        return jsonify({"error": "Comment not found."}), 404

    comment_data = {
        "comment_id": comment.comment_id,
        "content": comment.content,
        "created_at": comment.created_at,
    }

    return jsonify(comment_data), 200


@comments_bp.route("/<string:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    data = request.json
    comment = repo.match(Comment, comment_id).first()

    if comment is None:
        return jsonify({"error": "Comment not found"}), 404

    if "content" in data:
        comment.content = data["content"]

    repo.save(comment)
    return jsonify({"message": "Comment succesfully updated"}), 201


@comments_bp.route("/<string:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = repo.match(Comment, comment_id).first()

    if comment is None:
        return jsonify({"error": "Comment not found"}), 404

    repo.delete(comment)
    return jsonify(), 204


@comments_bp.route("/<string:comment_id>/like", methods=["POST"])
def add_like(comment_id):
    data = request.json
    if "user_id" not in data:
        return jsonify({"error": "user_id property is missing"}), 400

    user = repo.match(User, data["user_id"]).first()
    if user is None:
        return jsonify({"error": "User not found."}), 404

    comment = repo.match(Comment, comment_id).first()
    if comment is None:
        return jsonify({"error": "Comment not found."}), 404

    user.comments_likes.add(comment)
    repo.save(user)
    return (
        jsonify({"message": f"Comment succesfully liked by User {user.user_id}"}),
        201,
    )


@comments_bp.route("/<string:comment_id>/like", methods=["DELETE"])
def remove_like(comment_id):
    data = request.json
    if "user_id" not in data:
        return jsonify({"error": "user_id property is missing"}), 400

    user = repo.match(User, data["user_id"]).first()
    if user is None:
        return jsonify({"error": "User not found."}), 404

    comment = repo.match(Comment, comment_id).first()
    if comment is None:
        return jsonify({"error": "Comment not found."}), 404

    user.comments_likes.remove(comment)
    repo.save(user)
    return (
        jsonify({"message": f"Comment succesfully unliked by User {user.user_id}"}),
        201,
    )
