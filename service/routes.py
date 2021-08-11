"""
Promotion  Service
Paths:
------
GET /promotions - Returns a list all of the Promotions
GET /promotions/{id} - Returns the Promotion with a given id number
POST /promotions - creates a new Promotion record in the database
PUT /promotions/{id} - updates a Promotion record in the database
DELETE /promotions/{id} - deletes a Promotion record in the database
PUT /promotions/{id}/activate - activates a Promotion with a given id number
PUT /promotions/{id}/deactivate - deactivates a Promotion with a given id number
"""

import os
import sys
import uuid
import logging
from functools import wraps
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_restx import Api, Resource, fields, reqparse, inputs
from werkzeug.exceptions import NotFound
from . import status  # HTTP Status Codes


# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Promotion, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Promotions REST API Service',
          description='This is a promotions server.',
          default='promotions',
          default_label='Promotion operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
         )


# Define the model so that the docs reflect what can be sent
create_model = api.model('Promotion', {
    'title': fields.String(required=True,
                          description='The name of the Promotion'),
    'promotion_type': fields.String(required=True,
                              description='The type of promotion (Buy one Get one Free)'),
    'start_date': fields.DateTime(required=True,
                              description='The start date of the promotion'),
    'end_date': fields.DateTime(required=True,
                              description='The end date of the promotion'),
    'active': fields.Boolean(required=True,
                                description='Is the promotion active?')
})

promotion_model = api.inherit(
    'PromotionModel', 
    create_model,
    {
        'id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)


# query string arguments
promotion_args = reqparse.RequestParser()
promotion_args.add_argument('title', type=str, required=False, location='args', help='List Promotions by title')
promotion_args.add_argument('promotion_type', type=str, required=False,location='args', help='List Promotions by type')
promotion_args.add_argument('end_date', type=inputs.datetime_from_iso8601, required=False,location='args', help='List Promotions by type')
promotion_args.add_argument('active', type=inputs.boolean, required=False,location='args', help='List Promotions by active status')




######################################################################
# PATH: /promotions/{id}
######################################################################
@api.route('/promotions/<promotion_id>')
@api.param('promotion_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource Class
    
    Allows manipulation of a single Promotion with id
    GET /promotion{id} - Returns promotion with given id
    PUT /promotion{id} - Update promotion with given id
    DELETE /promotion{id} - Delete promotion with given id
    """
    ######################################################################
    # RETRIEVE A PROMOTION
    ######################################################################
    @api.doc('get_promotions')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single Promotion
        This endpoint will return a Promotion based on it's id
        """
        app.logger.info("Request for promotion with id: [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            raise NotFound(
                "Promotion with id '{}' was not found.".format(promotion_id))        
        return promotion.serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE AN EXISTING PROMOTION
    ######################################################################
    @api.response(404, 'Promotion not found')
    @api.response(400, 'The posted Promotion data was not valid')
    @api.doc('update_promotions')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion
        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to update promotion with id: [%s]", promotion_id)
        # check_content_type("application/json")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            raise NotFound(
                "Promotion with id '{}' was not found.".format(promotion_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        promotion.deserialize(data)
        promotion.id = promotion_id
        promotion.update()

        app.logger.info("Promotion with ID [%s] updated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A PROMOTION
    ######################################################################
    @api.doc('delete_promotions')
    @api.response(204, 'Promotion deleted')
    def delete(self, promotion_id):
        """
        Delete a Promotion
        This endpoint will delete a Promotion based the id specified in the path
        """
        app.logger.info("Request to delete promotion with id: [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
            app.logger.info("Promotion with ID [%s] delete complete.", promotion_id)
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions
######################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
######################################################################
# LIST ALL PROMOTIONS
######################################################################

    @api.doc('list_promotions')
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """ Returns all of the Promotions """
        app.logger.info("Request for promotion list")
        promotions = []
        args = promotion_args.parse_args()
        
        if args['promotion_type']:
            app.logger.info('Filtering by promotion type: %s', args['promotion_type'])
            promotions = Promotion.find_by_promotiontype(args['promotion_type'])
        elif args['active'] is not None:
            app.logger.info('Filtering by active: %s', args['active'])
            promotions = Promotion.find_by_active(args['active'])
        elif args['title']:
            app.logger.info('Filtering by title: %s', args['title'])
            promotions = Promotion.find_by_title(args['title'])
        elif args['end_date']:
            app.logger.info('Filtering by end date: %s', args['end_date'])
            promotions = Promotion.find_by_end_date(args['end_date'])
        else:
            app.logger.info('Returning unfiltered list.')
            promotions = Promotion.all()

        
        results = [promotion.serialize() for promotion in promotions]
        app.logger.info('[%s] Promotions returned', len(results))
        return results, status.HTTP_200_OK


######################################################################
# ADD A NEW PROMOTION
######################################################################

    @api.doc('create_promotions')
    @api.response(400, 'The posted data was not valid')
    @api.response(415, 'Invalid Content Type')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Creates a Promotion
        This endpoint will create a Promotion based the data in the body that is posted
        """
        app.logger.info("Request to create a promotion")
        promotion = Promotion()
        check_content_type("application/json")
        app.logger.debug('Payload = %s', api.payload)
        # if not api.payload:
        #     abort(status.HTTP_400_BAD_REQUEST, 'Bad Request')
        try:
            promotion.deserialize(api.payload)
            if promotion.title and promotion.promotion_type and promotion.start_date and promotion.end_date:
                promotion.create()
            app.logger.info('Promotion with new id [%s] created!', promotion.id)
            location_url = api.url_for(PromotionResource, promotion_id=promotion.id, _external=True)
            return promotion.serialize(), status.HTTP_201_CREATED, {'Location': location_url}
        except Exception:
            api.abort(status.HTTP_400_BAD_REQUEST, 'Bad Request')
        
            

        
        

######################################################################
#  PATH: /promotions/{id}/activate
######################################################################
@api.route('/promotions/<promotion_id>/activate')
@api.param('promotion_id', 'The Promotion identifier')
class ActivateResource(Resource):
    """ Activate actions on a Promotion """ 
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    @api.doc('activate_promotions')
    def put(self, promotion_id):
       
        app.logger.info("Request to activate promotion with id: %s", promotion_id)
        # check_content_type("application/json")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            raise NotFound(
            "Promotion with id '{}' was not found.".format(promotion_id))
        promotion.active = True
        promotion.update()

        app.logger.info("Promotion with ID [%s] has been activated!", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK




######################################################################
#  PATH: /promotions/{id}/deactivate
######################################################################
@api.route('/promotions/<promotion_id>/deactivate')
@api.param('promotion_id', 'The Promotion identifier')
class DeactivateResource(Resource):
    """ Deactivate actions on a Promotion """
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    @api.doc('deactivate_promotions')
    def put(self, promotion_id):
        app.logger.info(
            "Request to deactivate promotion with id: %s", promotion_id)
        # check_content_type("application/json")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            raise NotFound(
            "Promotion with id '{}' was not found.".format(promotion_id))
        promotion.active = False
        promotion.update()

        app.logger.info("Promotion with ID [%s] has been deactivated!", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)



# load sample data
def data_load(payload):
    promotion = Promotion(payload['title'], payload['promotion_type'], payload['start_date'], payload['end_date'], payload['active'])
    promotion.create()




def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Promotion.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error(
        "Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          "Content-Type must be {}".format(content_type))
