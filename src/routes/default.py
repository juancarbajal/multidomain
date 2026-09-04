"""Routes of the web server."""

from flask import request, jsonify

# from flask_jwt_extended import jwt_required
from flask_expects_json import expects_json

# from flask_cors import CORS, cross_origin
import json
from playhouse.shortcuts import model_to_dict

# import re
# import sys
# from os.path import exists
from . import routes_api
from multidomain import environment
from multidomain.constants import Constants
from multidomain.model.domain import DomainModel

# sys.path.append('../multidomain')

schemaValidateDomain = {
    "type": "object",
    "properties": {"domain": {"type": "string"}},
    "required": ["domain"],
}
schemaCreateDomain = {
    "type": "object",
    "properties": {
        "company_id": {"type": "string"},
        "domain": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "phone": {"type": "string"},
        "fax": {"type": "string"},
        "email": {"type": "string"},
        "org_name": {"type": "string"},
        "address1": {"type": "string"},
        "address2": {"type": "string"},
        "address3": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "country": {"type": "string"},
        "postal_code": {"type": "string"},
        "document_type": {"type": "string"},
        "document_number": {"type": "string"},
    },
    "required": [
        "company_id",
        "domain",
        "first_name",
        "last_name",
        "phone",
        "fax",
        "email",
        "org_name",
        "address1",
        "address2",
        "city",
        "state",
        "country",
        "postal_code",
    ],
}
schemaUpdateDomain = {
    "type": "object",
    "properties": {
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "phone": {"type": "string"},
        "fax": {"type": "string"},
        "email": {"type": "string"},
        "org_name": {"type": "string"},
        "address1": {"type": "string"},
        "address2": {"type": "string"},
        "address3": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "country": {"type": "string"},
        "postal_code": {"type": "string"},
        "document_type": {"type": "string"},
        "document_number": {"type": "string"},
    },
    "required": [
        "first_name",
        "last_name",
        "phone",
        "fax",
        "email",
        "org_name",
        "address1",
        "address2",
        "city",
        "state",
        "country",
        "postal_code",
    ],
}

env = environment.Environment()
tucowsConnection = env.getTucowsConnection()
dbConnection = env.getDbConnection()
statusRecorder = env.getStatusRecorder()


@routes_api.route("/public/v1/health")
def ping():
    """
    Health of the services.

    Returns:
        a json message if system is run
    """
    try:
        global env
        return jsonify(message="Domain Registration service v" + env.getAppVersion())
    except Exception:
        return jsonify(message="database don't exists, check .env file")


@routes_api.route("/internal/domain/create", methods=["POST"])
@expects_json(schemaCreateDomain)
def createDomain():
    """
    Create domain.

    Returns:
        a json message if the process to create Domain init
    """
    try:
        domain = (
            request.json.pop("domain")
            .replace("https://", "")
            .replace("http://", "")
            .replace("www.", "")
        )
        companyId = request.json.pop('company_id')
        global statusRecorder
        resFree, msgFree = tucowsConnection.isFreeDomain(domain)
        if resFree == 0:
            d = DomainModel()
            res, msg = d.createDomain(companyId, domain, json.dumps(request.json))
            if res == 0:
                statusRecorder.register(
                    companyId, domain, Constants.REGISTRATION_STATUS_PENDING
                )
                return jsonify(message="process started")
            else:
                return jsonify(message=msg.__str__()), 400
        else:
            return jsonify(message=msgFree), 400
    except Exception as e:
        return jsonify(message=e), 400


@routes_api.route("/auth/domain/validate", methods=["POST"])
@expects_json(schemaValidateDomain)
def validateDomain():
    """
    Validate if the domain is free to use.

    Returns:
       message(str): Ok or error message
       code(int): Status code
    """
    try:
        domain = request.json["domain"]
        global tucowsConnection
        res, msg = tucowsConnection.isFreeDomain(domain)
        if res == 0:
            return jsonify(message="Ok")
        else:
            resSuggestion, dataSuggestion = tucowsConnection.getSuggestions(domain)
            return jsonify(message=msg, data=dataSuggestion), 400
    except Exception as e:
        return json(message=e), 400


@routes_api.route("/auth/companies/<id>/domains", methods=["GET"])
def getDomain(id):
    """
    Get Domain information.

    Returns:
        message(str): Ok or error message
        code(int): Status code
    """
    try:
        d = DomainModel()
        r = d.getDomainByCompany(str(id))
        if r is None:
            return jsonify(message="No records"), 400
        else:
            r = model_to_dict(r)
            r['owner'] = json.loads(r['owner'])
            return jsonify(message="Ok", data=r)
    except Exception as e:
        return json(message=e), 400


@routes_api.route("/auth/companies/<id>/domains", methods=["PUT"])
@expects_json(schemaUpdateDomain)
def putDomain(id):
    """
    Put Domain information.

    Returns:
        message(str): Ok or error message
        code(int): Status code
    """
    try:
        d = DomainModel()
        d.updDomainOwner(id, json.dumps(request.json))
        return jsonify(message='Ok')
    except Exception as e:
        return json(message=e), 400

# @routes_api.route('/auth/domain/status')
# def status():
#     """
#     status
#     @return: a json with the status ['pending', 'completed', 'none'] for the domain registration of a company
#     """
#     try:
#         global env
#         global dbConnection
#         companyId = request.args.get('companyId')
        
#         res, msg = dbConnection.status(companyId)

#         if res == 0:
#             status = 'pending'

#             if msg == 'finished'
#                 status = 'completed'
#             return jsonify(status=status)
#         else:
#             return jsonify(status='none')
#     except Exception as e:
#         return jsonify(message = "database don't exists, check .env file")
