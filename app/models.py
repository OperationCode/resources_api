from sqlalchemy_utils import URLType

from app import db

'''
    event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event')
    partner_id = db.Column('partner_id', db.Integer, db.ForeignKey('partner.id'))
    partner = db.relationship('Partner')

'''

language_identifier = db.Table('language_identifier',
    db.Column('resource_id', db.Integer, db.ForeignKey('resource.id')),
    db.Column('language_id', db.Integer, db.ForeignKey('language.id'))
)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(URLType, nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
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
       return {
           'id'            : self.id,
           'name'          : self.name,
           'url'           : self.url,
           'category'      : self.category.name,
           'languages'     : self.serialize_languages,
           'paid'          : self.paid,
           'notes'         : self.notes,
           'upvotes'       : self.upvotes,
           'downvotes'     : self.downvotes,
           'times_clicked' : self.times_clicked
       }

    @property
    def serialize_languages(self):
        return [ lang.name for lang in self.languages ]

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
        return f"<Resource \n\tName: {self.name}\n\tLanguages: {self.languages}\n\tCategory: {self.category}\n\tURL: {self.url}\n>"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

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
