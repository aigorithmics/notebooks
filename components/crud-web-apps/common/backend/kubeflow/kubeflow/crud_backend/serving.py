import logging

import os
from flask import Blueprint, Response, current_app, send_from_directory

from . import csrf, helpers

bp = Blueprint("serving", __name__)
log = logging.getLogger(__name__)

# Caching: We want the browser to always check if the index.html file it has
# is the latest one. Also we want this check to use the ETag header and not
# the Last-Modified since our app will be served inside a container and we
# might want to roll-back.
# The JS/CSS files will have a hash in their name and thus we will want to
# cache them for as long as possible


@bp.route("/index.html")
@bp.route("/")
@bp.route("/<path:path>")
def serve_index(path="/"):
    # Check if the requested path is an existing static file (e.g. main.js that Angular generates)
    # This replaces the need for --deploy-url static/ in the frontend build.
    if path != "/":
        static_dir = current_app.config.get("STATIC_DIR")
        if static_dir and os.path.isfile(os.path.join(static_dir, path)):
            return send_from_directory(static_dir, path)

    # Serve the index file in all other cases
    log.info("Serving index.html for path: %s", path)

    no_cache = "no-cache, no-store, must-revalidate, max-age=0"
    resp = Response(
        helpers.get_prefixed_index_html(),
        mimetype="text/html",
        headers={"Cache-Control": no_cache},
    )

    csrf.set_cookie(resp)

    return resp
