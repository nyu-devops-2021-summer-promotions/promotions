"""
Promotion API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
  While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_service.py:TestPromotionServer
"""

import os
import json
import logging
import unittest
from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models import db
from service.routes import app, init_db
from .factories import PromotionFactory
from dateutil import parser

# # DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
# DATABASE_URI = os.getenv(
#     "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
# )

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

# override if we are running in Cloud Foundry
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']
  
BASE_URL = "/promotions"
CONTENT_TYPE_JSON = "application/json"
######################################################################
#  T E S T   C A S E S
######################################################################


class TestPromotionServer(unittest.TestCase):
    """ Promotion Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_promotions(self, count):
        """ Factory method to create promotions in bulk """
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            resp = self.app.post(
                "/promotions", json=test_promotion.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = resp.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Promotion REST API Service", resp.data)
      
    def test_get_promotion_list(self):
        """ Get a list of Promotions """
        self._create_promotions(5)
        resp = self.app.get("/promotions")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_promotion(self):
        """ Get a single Promotion """
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.get(
            "/promotions/{}".format(test_promotion.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["title"], test_promotion.title)

    def test_get_promotion_not_found(self):
        """ Get a Promotion thats not found """
        resp = self.app.get("/promotions/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_promotion(self):
        """ Create a new Promotion """
        test_promotion = PromotionFactory()
        logging.debug(test_promotion)
        resp = self.app.post(
            "/promotions", json=test_promotion.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_promotion = resp.get_json()
        self.assertEqual(new_promotion["title"],
                         test_promotion.title, "Title do not match")
        self.assertEqual(
            new_promotion["promotion_type"], test_promotion.promotion_type, "Promotion Type do not match"
        )
        self.assertEqual(
            parser.parse(new_promotion["start_date"]).strftime(
                '%Y-%m-%d'), test_promotion.start_date, "Start date does not match"
        )
        self.assertEqual(
            parser.parse(new_promotion["end_date"]).strftime(
                '%Y-%m-%d'), test_promotion.end_date, "End date does not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_promotion = resp.get_json()
        self.assertEqual(new_promotion["title"],
                         test_promotion.title, "Title do not match")
        self.assertEqual(
            new_promotion["promotion_type"], test_promotion.promotion_type, "Promotion Type do not match"
        )
        self.assertEqual(
            parser.parse(new_promotion["start_date"]).strftime(
                '%Y-%m-%d'), test_promotion.start_date, "Start date does not match"
        )
        self.assertEqual(
            parser.parse(new_promotion["end_date"]).strftime(
                '%Y-%m-%d'), test_promotion.end_date, "End date does not match"
        )

    def test_create_promotion_no_data(self):
        """ Create a Promotion with missing data """
        resp = self.app.post(
            "/promotions", json={}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_no_content_type(self):
        """ Create a Promotion with no content type """
        resp = self.app.post("/promotions")

        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_promotion(self):
        """Update an existing Promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post(
            BASE_URL, json=test_promotion.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = resp.get_json()
        logging.debug(new_promotion)
        new_promotion["title"] = "unknown"
        resp = self.app.put(
            "/promotions/{}".format(new_promotion["id"]),
            json=new_promotion,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion["title"], "unknown")

        resp = self.app.put(
            "/promotions/{}".format(int(new_promotion["id"])+1),
            json=new_promotion,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_promotion(self):
        """Activate an existing Promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post(
            BASE_URL, json=test_promotion.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the promotion
        new_promotion = resp.get_json()
        logging.debug(new_promotion)
        new_promotion["active"] = False
        self.assertEqual(new_promotion["active"], False)
        resp = self.app.put(
            "/promotions/{}/activate".format(new_promotion["id"]),
            json=new_promotion,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion["active"], True)
        resp = self.app.put(
            "/promotions/{}/activate".format(int(new_promotion["id"])+1),
            json=new_promotion,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_deactivate_promotion(self):
        """Deactivate an existing Promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post(
            BASE_URL, json=test_promotion.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = resp.get_json()
        logging.debug(new_promotion)
        new_promotion["active"] = True
        self.assertEqual(new_promotion["active"], True)
        resp = self.app.put(
            "/promotions/{}/deactivate".format(new_promotion["id"]),
            json=new_promotion,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion["active"], False)

        resp = self.app.put(
            "/promotions/{}/deactivate".format(int(new_promotion["id"])+1),
            json=new_promotion,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_promotion(self):
        """Delete a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, test_promotion.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_promotion.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_promotion_list_by_promotion_type(self):
        """Query Promotions by promotion_type"""
        promotions = self._create_promotions(10)
        test_promotion_type = promotions[0].promotion_type
        promotion_type_promotions = [promotion for promotion in promotions if promotion.promotion_type == test_promotion_type]
        resp = self.app.get(
            BASE_URL, query_string="promotion_type={}".format(quote_plus(test_promotion_type))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(promotion_type_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["promotion_type"], test_promotion_type)
    
    def test_query_promotion_list_by_active(self):
        """Query Promotions by Active"""
        promotions = self._create_promotions(10)
        test_active = promotions[0].active
        active_promotions = [promotion for promotion in promotions if promotion.active == test_active]
        resp = self.app.get(
            BASE_URL, query_string="active={}".format(test_active)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(active_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["active"], test_active)

    def test_query_promotion_list_by_title(self):
        """Query Promotions by Title"""
        promotions = self._create_promotions(10)
        test_title = promotions[0].title
        title_promotions = [promotion for promotion in promotions if promotion.title == test_title]
        resp = self.app.get(
            BASE_URL, query_string="title={}".format(quote_plus(test_title))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(title_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["title"], test_title)
            

    def test_query_promotion_list_by_end_date(self):
        """Query Promotions by End Date"""
        promotions = self._create_promotions(10)
        test_end_date = promotions[0].end_date
        end_date_promotions = [promotion for promotion in promotions if promotion.end_date == test_end_date]
        resp = self.app.get(
            BASE_URL, query_string="end_date={}".format(test_end_date)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(end_date_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(parser.parse(promotion["end_date"]).
                            strftime('%Y-%m-%d'),
                             test_end_date)
