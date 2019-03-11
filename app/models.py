from app import db
from sqlalchemy_utils import URLType
from sqlalchemy import DateTime
from sqlalchemy.sql import func


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
    paid = db.Column(db.Boolean, default=False)
    notes = db.Column(db.String)
    upvotes = db.Column(db.INTEGER, default=0)
    downvotes = db.Column(db.INTEGER, default=0)
    times_clicked = db.Column(db.INTEGER, default=0)

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
            'paid': self.paid,
            'notes': self.notes,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'times_clicked': self.times_clicked,
            'created_at': created,
            'last_updated': updated
        }

    @property
    def serialize_languages(self):
        return [lang.name for lang in self.languages]

    def key(self):
        return self.url

    def __eq__(self, other):
        if isinstance(other, Resource):
            if self.name != other.name:
                return False
            if self.url != other.url:
                return False
            if self.paid != other.paid:
                return False
            if self.notes != other.notes:
                return False
            if self.category != other.category:
                return False
            if self.languages != other.languages:
                return False
            return True
        return False

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
        return f"<Key email={self.email} apikey={self.apikey}>"
