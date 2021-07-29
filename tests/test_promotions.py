"""
Test cases for Promotion Model
Test cases can be run with:
    nosetests
    coverage report -m
While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_promotionss.py:TestPromotionModel
"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Promotion, DataValidationError, db
from service import app
from .factories import PromotionFactory
from dateutil import parser

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  P R O M O T I O N   M O D E L   T E S T   C A S E S
######################################################################


class TestPromotionModel(unittest.TestCase):
    """ Test Cases for Promotion Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_promotion(self):
        """ Create a promotion and assert that it exists """
        promotion = Promotion(title="Winter Sale", promotion_type="30%OFF",
                              start_date="2021-11-01", end_date="2021-12-24")
        self.assertTrue(promotion != None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.title, "Winter Sale")
        self.assertEqual(promotion.promotion_type, "30%OFF")
        self.assertEqual(promotion.start_date, "2021-11-01")
        self.assertEqual(promotion.end_date, "2021-12-24")

    def test_add_a_promotion(self):
        """ Create a promotion and add it to the database """
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(title="Winter Sale", promotion_type="30%OFF",
                              start_date="2021-11-01", end_date="2021-12-24")
        self.assertTrue(promotion != None)
        self.assertEqual(promotion.id, None)
        promotion.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(promotion.id, 1)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_update_a_promotion(self):
        """Update a Promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.create()
        logging.debug(promotion)
        self.assertEqual(promotion.id, 1)
        # Change it an save it
        promotion.title = "test"
        original_id = promotion.id
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.title, "test")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].id, 1)
        self.assertEqual(promotions[0].title, "test")

    def test_delete_a_promotion(self):
        """Delete a Promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_serialize_a_promotion(self):
        """ Test serialization of a Promotion """
        promotion = PromotionFactory()
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], promotion.id)
        self.assertIn("title", data)
        self.assertEqual(data["title"], promotion.title)
        self.assertIn("promotion_type", data)
        self.assertEqual(data["promotion_type"], promotion.promotion_type)
        self.assertIn("start_date", data)
        self.assertEqual(data["start_date"], promotion.start_date)
        self.assertIn("end_date", data)
        self.assertEqual(data["end_date"], promotion.end_date)

    def test_deserialize_a_promotion(self):
        """ Test deserialization of a Promotion """
        data = {
            "id": 1,
            "title": "Happy Sale",
            "promotion_type": "Free delivery",
            "start_date": "2021-07-01",
            "end_date": "2021-07-14",
            "active": True,

        }
        promotion = Promotion()
        promotion.deserialize(data)
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.title, "Happy Sale")
        self.assertEqual(promotion.promotion_type, "Free delivery")
        self.assertEqual(promotion.start_date, "2021-07-01")
        self.assertEqual(promotion.end_date, "2021-07-14")
        self.assertEqual(promotion.active, True)

    def test_deserialize_missing_data(self):
        """ Test deserialization of a Promotion with missing data """
        data = {"id": 1, "title": "Happy Sale",
                "promotion_type": "Free delivery"}
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_find_promotion(self):
        """Find a Promotion by ID"""
        promotions = PromotionFactory.create_batch(3)
        for promotion in promotions:
            promotion.create()
        logging.debug(promotions)
        # make sure they got saved
        self.assertEqual(len(promotion.all()), 3)
        # find the 2nd promotion in the list
        promotion = Promotion.find(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.title, promotions[1].title)
        self.assertEqual(promotion.promotion_type,
                         promotions[1].promotion_type)
        self.assertEqual(promotion.start_date, promotions[1].start_date)
        self.assertEqual(promotion.end_date, promotions[1].end_date)

    def test_find_by_promotion_type(self):
        """Find a Promotion by promotion_type"""
        Promotion(title="Summer Sale", promotion_type="10%OFF",
                  start_date="2021-07-01", end_date="2021-08-31", active=True).create()
        Promotion(title="Winter Sale", promotion_type="20%OFF",
                  start_date="2021-12-01", end_date="2021-12-31", active=False).create()
        promotions = Promotion.find_by_promotiontype("20%OFF")
        self.assertEqual(promotions[0].title, "Winter Sale")
        self.assertEqual(promotions[0].promotion_type, "20%OFF")
        self.assertEqual(promotions[0].start_date.strftime(
            '%Y-%m-%d'), "2021-12-01")
        self.assertEqual(promotions[0].end_date.strftime(
            '%Y-%m-%d'), "2021-12-31")
        self.assertEqual(promotions[0].active, False)

    def test_find_by_active(self):
        """Find a Promotion by active"""
        Promotion(title="Summer Sale", promotion_type="10%OFF",
                  start_date="2021-07-01", end_date="2021-08-31", active=True).create()
        Promotion(title="Winter Sale", promotion_type="20%OFF",
                  start_date="2021-12-01", end_date="2021-12-31", active=False).create()
        promotions = Promotion.find_by_active(False)
        self.assertEqual(promotions[0].title, "Winter Sale")
        self.assertEqual(promotions[0].promotion_type, "20%OFF")
        self.assertEqual(promotions[0].start_date.strftime(
            '%Y-%m-%d'), "2021-12-01")
        self.assertEqual(promotions[0].end_date.strftime(
            '%Y-%m-%d'), "2021-12-31")
        self.assertEqual(promotions[0].active, False)

    def test_find_or_404_found(self):
        """Find or return 404 found"""
        promotions = PromotionFactory.create_batch(3)
        for promotion in promotions:
            promotion.create()

        promotion = Promotion.find_or_404(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.title, promotions[1].title)
        self.assertEqual(promotion.promotion_type,
                         promotions[1].promotion_type)
        self.assertEqual(promotion.start_date, promotions[1].start_date)
        self.assertEqual(promotion.end_date, promotions[1].end_date)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, Promotion.find_or_404, 0)

    def test_find_by_promotion_title(self):
        """Find a Promotion by title"""
        Promotion(title="Summer Sale", promotion_type="10%OFF",
                  start_date="2021-07-01", end_date="2021-08-31", active=True).create()
        Promotion(title="Winter Sale", promotion_type="20%OFF",
                  start_date="2021-12-01", end_date="2021-12-31", active=False).create()
        promotions = Promotion.find_by_title("Winter Sale")
        self.assertEqual(promotions[0].title, "Winter Sale")
        self.assertEqual(promotions[0].promotion_type, "20%OFF")
        self.assertEqual(promotions[0].start_date.strftime(
            '%Y-%m-%d'), "2021-12-01")
        self.assertEqual(promotions[0].end_date.strftime(
            '%Y-%m-%d'), "2021-12-31")
        self.assertEqual(promotions[0].active, False)

    def test_find_by_promotion_end_date(self):
        """Find a Promotion by end_date"""
        Promotion(title="Summer Sale", promotion_type="10%OFF",
                  start_date="2021-07-01", end_date="2021-08-31", active=True).create()
        Promotion(title="Winter Sale", promotion_type="20%OFF",
                  start_date="2021-12-01", end_date="2021-12-31", active=False).create()
        promotions = Promotion.find_by_end_date("2021-12-31")
        self.assertEqual(promotions[0].title, "Winter Sale")
        self.assertEqual(promotions[0].promotion_type, "20%OFF")
        self.assertEqual(promotions[0].start_date.strftime(
            '%Y-%m-%d'), "2021-12-01")
        self.assertEqual(promotions[0].end_date.strftime(
            '%Y-%m-%d'), "2021-12-31")
        self.assertEqual(promotions[0].active, False)
