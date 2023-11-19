import logging, os, json
from functools import wraps
from flask import g

from error_handler import AccessDeniedException, SystemFailureException

logger = logging.getLogger(__name__)

def load_event_from_json(filename):
  """
  Loads a test event from a file
  """
  logger.info(f"load_event_from_json: loading from {filename}")
  f = open(filename)
  data = json.load(f)
  return data

def get_username(f):
  """
  Decorator which gets the username (email claim) from the JWT in the app context event
  """
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """
    Function which gets the email claim from the app context

    If the event is missing from the event context this will fail
    """
    logger.info("get_username has started")
    if "event" not in g:
      logger.error("get_username: event missing from app context")
      raise SystemFailureException("Event is missing from app context")
    else:
      logger.error("get_username: event is present in the app context")
      if "requestContext" in g.event:
        rc = g.event["requestContext"]
        if "authorizer" in rc:
          a = rc["authorizer"]
          if "claims" in a:
            # we got the claims
            claims = a["claims"]
            if "email" in claims:
              email = claims["email"]
              logger.info(f"get_username: got email of {email}")
              return f(email, *args, **kwargs)
          else:
            logger.error("get_username: cannot find in claims")
        else:
          logger.error("get_username: cannot find authorizer")
      else:
        logger.error("get_username: cannot find requestContext")
    raise SystemFailureException("Event is malformed")

  return decorated_function

def inject_event(f):
  """
  Decorator which injects a test event into the request context if there are none present
  """
  @wraps(f)
  def decorated_function(*args, **kwargs):
    """
    Function to check if the event is present

    If there's no NON_PROD environment variable set this will fail
    """
    logger.info("inject_event has started")
    if "event" not in g:
      if "NON_PROD" not in os.environ:
        logger.info("inject_event: no event in app context and not in NON_PROD mode")
        raise AccessDeniedException("No JWT claims available")
      logger.info("inject_event: no event in app context, loading from event.json")
      event = load_event_from_json("event.json")
      g.event = event
      logger.info("inject_event: event injected")
    else:
      logger.info("inject_event: event is already present in the app context")
    return f(*args, **kwargs)
  
  return decorated_function

