from app import db
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy_utils import URLType
from flask_security import RoleMixin, UserMixin

language_identifier = db.Table('language_identifier',
                               db.Column(
                                   'resource_id',
                                   db.Integer,
                                   db.ForeignKey('resource.id')),
                               db.Column(
                                   'language_id',
                                   db.Integer,
                                   db.ForeignKey('language.id'))
                               )


class TimestampMixin:
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(DateTime(timezone=True), onupdate=func.now())


class Resource(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(URLType, nullable=False, unique=True)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('category.id'),
                            nullable=False)
    category = db.relationship('Category')
    languages = db.relationship('Language', secondary=language_identifier)
    free = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.String)
    upvotes = db.Column(db.INTEGER, default=0)
    downvotes = db.Column(db.INTEGER, default=0)
    times_clicked = db.Column(db.INTEGER, default=0)
    voters = db.relationship('VoteInformation', back_populates='resource')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        if self.created_at:
            created = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            created = ""
        if self.last_updated:
            updated = self.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        else:
            updated = ""

        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'category': self.category.name,
            'languages': self.serialize_languages,
            'free': self.free,
            'notes': self.notes,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'times_clicked': self.times_clicked,
            'created_at': created,
            'last_updated': updated
        }

    @property
    def serialize_algolia_search(self):
        result = self.serialize
        result['objectID'] = self.id
        return result

    @property
    def serialize_languages(self):
        return [lang.name for lang in self.languages]

    def key(self):
        return self.url

    def __eq__(self, other):
        return isinstance(other, Resource) and all(
            (
                getattr(self, attribute)
                == getattr(other, attribute)
                for attribute in [
                    "name",
                    "url",
                    "free",
                    "notes",
                    "category",
                    "languages",
                ]
            )
        )

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        return (f"<Resource \n"
                f"\tName: {self.name}\n"
                f"\tLanguages: {self.languages}\n"
                f"\tCategory: {self.category}\n"
                f"\tURL: {self.url}\n>")


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }

    def key(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Category):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"<Category {self.name}>"


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }

    def key(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Language):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"<Language {self.name}>"


class Key(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apikey = db.Column(db.String, unique=True, nullable=False, index=True)
    email = db.Column(db.String, unique=True, nullable=False)
    denied = db.Column(db.Boolean, default=False)
    voted_resources = db.relationship('VoteInformation', back_populates='voter')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        if self.created_at:
            created = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            created = ""
        if self.last_updated:
            updated = self.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        else:
            updated = ""
        return {
            'apikey': self.apikey,
            'email': self.email,
            'created_at': created,
            'last_updated': updated
        }

    def __eq__(self, other):
        if isinstance(other, Key):
            return self.apikey == other.apikey
        return False

    def __hash__(self):
        return hash(self.apikey)

    def __repr__(self):
        tags = ''
        if self.denied:
            tags = ' DENIED'
        return f"<Key email={self.email} apikey={self.apikey}{tags}>"


class VoteInformation(db.Model):
    voter_apikey = db.Column(db.String, db.ForeignKey('key.apikey'), primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), primary_key=True)
    current_direction = db.Column(db.String, nullable=False)
    resource = db.relationship('Resource', back_populates='voters')
    voter = db.relationship('Key', back_populates='voted_resources')


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


# Role class
class Role(db.Model, RoleMixin):
    # Our Role has three fields, ID, name and description
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception
    # TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


# User class
class User(db.Model, UserMixin):

    # Our User has six fields: ID, email, password, active, confirmed_at
    # and roles. The roles field represents a many-to-many relationship
    # using the roles_users table. Each user may have no role, one role,
    # or multiple roles.
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )
