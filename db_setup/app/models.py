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

    def __repr__(self):
        return f"<Resource \n\tName: {self.name}\n\tLanguages: {self.languages}\n\tCategory: {self.category}\n\tURL: {self.url}\n>"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Category {self.name}>"


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Language {self.name}>"
