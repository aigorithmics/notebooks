"""
Common helper functions for handling k8s objects information
"""

import datetime as dt
import logging
import os
import re

import yaml
from flask import current_app

log = logging.getLogger(__name__)


def get_prefixed_index_html():
    """
    The backend should modify the <base> element of the index.html file to
    align with the configured prefix the backend is listening
    """
    prefix = os.path.join("/", current_app.config["PREFIX"], "")
    static_dir = current_app.config["STATIC_DIR"]

    log.info("Setting the <base> to reflect the prefix: %s", prefix)
    with open(os.path.join(static_dir, "index.html"), "r") as f:
        index_html = f.read()
        index_prefixed = re.sub(
            r"\<base href=\".*\".*\>",
            '<base href="%s">' % prefix,
            index_html,
        )

        return index_prefixed


def load_yaml(f):
    """
    f: file path
    Load a yaml file and convert it to a python dict.
    """
    c = None
    try:
        with open(f, "r") as yaml_file:
            c = yaml_file.read()
    except IOError:
        log.error("Error opening: %s", f)
        return None

    try:
        contents = yaml.safe_load(c)
        if contents is None:
            # YAML exists but is empty
            return {}
        else:
            # YAML exists and is not empty
            return contents
    except yaml.YAMLError:
        return None


def load_param_yaml(f, **kwargs):
    """
    f: file path

    Load a yaml file and convert it to a python dict. The yaml might have some
    `{var}` values which the user will have to format. We load the YAML safely,
    and then traverse the dictionary to replace the `{var}` strings.
    """
    c = None
    try:
        with open(f, "r") as yaml_file:
            c = yaml_file.read()
    except IOError:
        log.error("Error opening: %s", f)
        return None

    try:
        contents = yaml.safe_load(c)
        if contents is None:
            return {}

        # Safely substitute variables after parsing
        return _substitute_variables(contents, kwargs)
    except yaml.YAMLError:
        return None


class _SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def _substitute_variables(data, kwargs):
    """
    Recursively traverse a parsed YAML dict/list and substitute {var} patterns
    with safely provided kwargs without exposing YAML injection.
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_data[key] = _substitute_variables(value, kwargs)
        return new_data
    elif isinstance(data, list):
        return [_substitute_variables(element, kwargs) for element in data]
    elif isinstance(data, str):
        # We only want to replace {var} syntax exactly as string.format would
        # but safely. We can use string.format on the individual values.
        try:
            # Use SafeDict so variables not in kwargs are left as {var}
            return data.format_map(_SafeDict(**kwargs))
        except Exception:
            pass
    return data


def get_uptime(then):
    """
    then: datetime instance | string

    Return a string that informs how much time has pasted from the provided
    timestamp.
    """
    if isinstance(then, str):
        then = dt.datetime.strptime(then, "%Y-%m-%dT%H:%M:%SZ")

    now = dt.datetime.now()
    diff = now - then.replace(tzinfo=None)

    days = diff.days
    hours = int(diff.seconds / 3600)
    mins = int((diff.seconds % 3600) / 60)

    age = ""
    if days > 0:
        if days == 1:
            age = str(days) + " day"
        else:
            age = str(days) + " days"
    else:
        if hours > 0:
            if hours == 1:
                age = str(hours) + " hour"
            else:
                age = str(hours) + " hours"
        else:
            if mins == 0:
                return "just now"
            if mins == 1:
                age = str(mins) + " min"
            else:
                age = str(mins) + " mins"

    return age + " ago"
