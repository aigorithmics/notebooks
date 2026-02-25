import functools
import logging

from flask import request
from werkzeug import exceptions

log = logging.getLogger(__name__)


def request_is_json_type(func):
    """Make sure that the current request is of type JSON"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if request.content_type != "application/json":
            raise exceptions.BadRequest("Request is not in JSON format.")

        return func(*args, **kwargs)

    return wrapper


def required_body_params(*params):
    """
    Used to decorate a route that accepts json and must contain some specific
    fields. If a field is not present then the server will return a 400 error.
    """

    def wrapper(func):
        @functools.wraps(func)
        def runner(*args, **kwargs):
            body = request.get_json()
            for param in params:
                if param not in body:
                    raise exceptions.BadRequest(
                        "Parameter '%s' is missing from the request's body." % param
                    )

            return func(*args, **kwargs)

        return runner

    return wrapper


def validate_kubernetes_name(func):
    """
    Validates that the 'name' parameter in the JSON body, if present,
    conforms to the Kubernetes DNS-1123 label constraints (RFC 1123).
    Additionally limits the name length to prevent DoS via massive payloads.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        body = request.get_json()
        if body and "name" in body:
            name = body["name"]
            if not isinstance(name, str):
                raise exceptions.BadRequest("Name must be a string.")

            if len(name) > 63:
                raise exceptions.BadRequest(
                    "Name is too long. Maximum allowed length is 63 characters."
                )

            # RFC 1123 label regex
            import re

            if not re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", name):
                raise exceptions.BadRequest(
                    "Name must consist of lower case alphanumeric characters "
                    "or '-', and must start and end with an alphanumeric character."
                )

        return func(*args, **kwargs)

    return wrapper
