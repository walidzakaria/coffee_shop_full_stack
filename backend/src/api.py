import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    """
    :returns all drinks in json format.
    No authentication nor authorization needed
    """
    drinks = Drink.query.all()

    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    }), 200


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    :returns: all drinks in json with detailed recipe
    only barista & managers can access it.
    """
    drinks = Drink.query.all()

    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    }), 200


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    """
    Creates a new drink.
    Only accessible for managers
    """
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        # Check if title and recipe included in the body
        if title is None or recipe is None:
            abort(422)

        # Create a new drink object
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()

        return jsonify({
            "success": True,
            "drinks": [new_drink.long()],
            "message": "Created Successfully"
        }), 200

    except:
        # In case of having errors
        abort(422)


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    """
    Updates existing drink by id
    Only accessible for managers
    """

    drink_to_update = Drink.query.filter_by(id=id).one_or_none()
    # Check if the drink with this id exists
    if drink_to_update is None:
        abort(404)
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    # Check if the body contains at least one of the needed fields
    if title is None and recipe is None:
        abort(422)

    try:
        # update the title if included in the request
        if title is not None:
            drink_to_update.title = title

        # update the recipe if included in the request
        if recipe is not None:
            drink_to_update.recipe = json.dumps(recipe)
        drink_to_update.update()

        return jsonify({
            "success": True,
            "drinks": [drink_to_update.long()]
        }), 200
    except:
        # In case of failure
        abort(422)


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    """
    Deletes an existing drink by id
    Only accessible for managers
    """
    drink_to_delete = Drink.query.filter_by(id=id).one_or_none()

    # Check if a drink with this id exists.
    if drink_to_delete is None:
        abort(404)
    try:
        drink_to_delete.delete()

        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except:
        # In case of failure
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


# I created this for bad json requests
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401


@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
