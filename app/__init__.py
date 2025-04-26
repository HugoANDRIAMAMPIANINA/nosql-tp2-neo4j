from flask import Flask
from py2neo import Graph
from py2neo.ogm import Repository
import config

graph = Graph(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
repo = Repository(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))


def create_app():
    app = Flask(__name__)

    from .routes.users import users_bp
    from .routes.posts import posts_bp
    from .routes.comments import comments_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)

    return app
