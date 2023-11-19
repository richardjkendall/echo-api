import logging
import sys
import json
#import boto3

import awsgi
from flask_cors import CORS
from flask import Flask, jsonify, make_response, request, g

from error_handler import error_handler, BadRequestException
from security import inject_event, get_username

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
logger.info("Starting...")

def success_json_response(payload):
  """
  Turns payload into a JSON HTTP200 response
  """
  response = make_response(jsonify(payload), 200)
  response.headers["Content-type"] = "application/json"
  return response

@app.route("/", methods=["POST"])
@error_handler
@inject_event
@get_username
def echo(username):
  """
  Echos back the request if it is JSON, otherwise returns an error
  """
  if request.json:
    payload = request.json
    payload["username"] = username
    return(success_json_response(payload))
  else:
    raise BadRequestException("Request must be JSON")

def lambda_handler(event, context):
  print("Event: {}".format(json.dumps(event)))
  g.event = event
  return awsgi.response(app, event, context, base64_content_types={"image/png"})

if __name__ == "__main__":
  logger.info("Starting as main")
  app.run(debug=True, port=5001, host="0.0.0.0", threaded=True)