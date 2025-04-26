from flask import Blueprint, request, jsonify
from py2neo import Node
from app import graph, repo
from app.models import Post, User, Comment

comments_bp = Blueprint("comments", __name__, url_prefix="/comments")


@comments_bp.route("", methods=["GET"])
def get_comments():
    """
    Get all comments
    ---
    tags:
      - Comments
    responses:
      200:
        description: A list of comments
        examples:
            application/json: [
                {
                    "comment_id": "fb8f24eb-01a9-4f49-b324-e34106c9f73c",
                    "content": "I am a good post comment :)",
                    "created_at": "1745676650"
                }
            ]
    """

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
    """
    Get a comment by its ID
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: A comment
        examples:
            application/json: {
                "comment_id": "fb8f24eb-01a9-4f49-b324-e34106c9f73c",
                "content": "I am a good post comment :)",
                "created_at": "1745676650"
            }
      404:
        description: Comment not found
    """

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
    """
    Update a comment
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            content:
              type: string
    responses:
      201:
        description: Comment succesfully updated
      404:
        description: Comment not found
    """

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
    """
    Delete a comment
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: string
        required: true
    responses:
      204:
        description: Comment succesfully deleted
      404:
        description: Comment not found
    """

    comment = repo.match(Comment, comment_id).first()

    if comment is None:
        return jsonify({"error": "Comment not found"}), 404

    repo.delete(comment)
    return jsonify(), 204


@comments_bp.route("/<string:comment_id>/like", methods=["POST"])
def add_like(comment_id):
    """
    Like a comment
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            user_id:
              type: string
    responses:
      201:
        description: Comment succesfully liked by user
      400:
        description: Missing user_id field
      404:
        description: User or Comment not found
    """

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
    """
    Unlike a comment
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            user_id:
              type: string
    responses:
      201:
        description: Comment succesfully unliked by user
      400:
        description: Missing user_id field
      404:
        description: User or Comment not found
    """

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
