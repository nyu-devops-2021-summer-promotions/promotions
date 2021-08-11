"""
Models for Promotion Service
All of the models are stored in this module
Models
------
Promotion - A Promotion is a representation of a special promotion 
or sale that is running against a product or perhaps the entire store
Attributes
-----------
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialies the SQLAlchemy app"""
    Promotion.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""



class Promotion(db.Model):
    """
    Class that represents a Promotion
    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app = None

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(63), nullable=False)
    promotion_type = db.Column(db.String(63), nullable=False)
    start_date = db.Column(db.DateTime(), nullable=False)
    end_date = db.Column(db.DateTime(), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return "<Promotion %r id=[%s]>" % (self.title, self.id)

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating %s", self.title)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Removes a Pet from the data store"""
        logger.info("Deleting %s", self.title)
        db.session.delete(self)
        db.session.commit()

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Updating %s", self.title)
        db.session.commit()

    def serialize(self):
        """Serializes a Promotion into a dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "promotion_type": self.promotion_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "active": self.active,
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary
        :param data: a dictionary of attributes
        :type data: dict
        :return: a reference to self
        :rtype: Promotion
        """
        try:
            self.title = data["title"]
            self.promotion_type = data["promotion_type"]
            self.start_date = data["start_date"]
            self.end_date = data["end_date"]
            self.active = data["active"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid promotion: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid promotion: body of request contained bad or no data"
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app):
        """Initializes the database session
        :param app: the Flask app
        :type data: Flask
        """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, promotion_id):
        """ Finds a Promotion by it's ID """
        logger.info("Processing lookup for id %s ...", promotion_id)
        try:
            val=int(promotion_id)
            return cls.query.get(promotion_id)
        except Exception:
            return('Bad Request')

    @classmethod
    def find_or_404(cls, promotion_id):
        """Find a Promotion by it's id

        :param promotion_id: the id of the Promotion to find
        :type promotion_id: int

        :return: an instance with the promotion_id, or 404_NOT_FOUND if not found
        :rtype: Promotion

        """
        logger.info("Processing lookup or 404 for id %s ...", promotion_id)
        return cls.query.get_or_404(promotion_id)

    @classmethod
    def find_by_promotiontype(cls, promotion_type):
        """Returns all Promotions with the given promotion_type

        Args:
            promotion_type (string): the promotion_type of the Promotions you want to match
        """
        logger.info("Processing promotion_type query for %s ...",
                    promotion_type)
        return cls.query.filter(cls.promotion_type == promotion_type)

    @classmethod
    def find_by_active(cls, active):
        """Returns all Promotions with the given active

            Args:
                active (boolean): the active of the Promotions you want to match
            """
        logger.info("Processing active query for %s ...",
                    active)
        return cls.query.filter(cls.active == active)

    @classmethod
    def find_by_title(cls, title):
        """Returns all Promotions with the given title

            Args:
                title (String): the active of the Promotions you want to match
            """
        logger.info("Processing active query for %s ...",
                    title)
        return cls.query.filter(cls.title == title)

    @classmethod
    def find_by_end_date(cls, end_date):
        """Returns all Promotions with the given end-date

            Args:
                end_date (Datetime): the active of the Promotions you want to match
            """
        logger.info("Processing active query for %s ...",
                    end_date)
        return cls.query.filter(cls.end_date == end_date)
