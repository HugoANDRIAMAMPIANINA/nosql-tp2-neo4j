from py2neo.ogm import Model, Property, RelatedTo, RelatedFrom
from py2neo.data import Relationship


class User(Model):
    __primarykey__ = "user_id"

    user_id = Property()
    name = Property()
    email = Property()
    created_at = Property()

    friends_with = RelatedTo("User", "FRIENDS_WITH")
    posts_likes = RelatedTo("Post", "LIKES")
    comments_likes = RelatedTo("Comment", "LIKES")
    posts_created = RelatedTo("Post", "CREATED")
    comments_created = RelatedTo("Comment", "CREATED")


class Post(Model):
    __primarykey__ = "post_id"

    post_id = Property()
    title = Property()
    content = Property()
    created_at = Property()

    has_comment = RelatedTo("Comment", "HAS_COMMENT")


class Comment(Model):
    __primarykey__ = "comment_id"

    comment_id = Property()
    content = Property()
    created_at = Property()


class Created(Relationship):
    pass


class HasComment(Relationship):
    pass


class FriendsWith(Relationship):
    pass


class Likes(Relationship):
    pass
