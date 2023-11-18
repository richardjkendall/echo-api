import logging
import sys
import json
#import boto3

import awsgi
from flask_cors import CORS
from flask import Flask, jsonify, make_response, request

from error_handler import error_handler, BadRequestException

#logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s')
app = Flask(__name__)
CORS(app)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
def echo():
  """
  Echos back the request if it is JSON, otherwise returns an error
  """
  if request.json:
    return(success_json_response(request.json))
  else:
    raise BadRequestException("Request must be JSON")

def lambda_handler(event, context):
  print("Event: {}".format(json.dumps(event)))
  return awsgi.response(app, event, context, base64_content_types={"image/png"})

if __name__ == "__main__":
  logger.info("Starting as main")
  app.run(debug=True, port=5001, host="0.0.0.0", threaded=True)