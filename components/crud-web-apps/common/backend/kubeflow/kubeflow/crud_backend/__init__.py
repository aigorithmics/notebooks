import logging

from flask import Flask

from . import settings
from .authn import bp as authn_bp
from .config import BackendMode
from .csrf import bp as csrf_bp
from .errors import bp as errors_bp
from .metrics import enable_metrics
from .probes import bp as probes_bp
from .routes import bp as base_routes_bp
from .serving import bp as serving_bp

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

# Content-Security-Policy for the Angular SPA.
# - frame-ancestors 'self': allows the Kubeflow central dashboard to embed
#   these apps in an iframe (same-origin), while blocking external sites.
# - worker-src blob:: required by Monaco editor for web workers.
# - style-src 'unsafe-inline': required by Angular Material for dynamic styles.
#
# WARNING [SECURITY EXCEPTION]: The inclusion of 'unsafe-inline' in style-src
# is a deliberate security compromise. Angular Material strictly requires this
# to compile and apply dynamic styles in the browser. While it weakens CSP
# protection against XSS and clickjacking, we accept this risk tradeoff
# because implementing CSP nonces is currently too disruptive to the Angular
# build pipeline. This should be addressed when Angular/build system upgrades
# allow straightforward CSP nonce generation for styles.
_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "font-src 'self' data:; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "connect-src 'self'"
)


def create_app(name, static_folder, config):
    logging.basicConfig(format=LOG_FORMAT, level=config.LOG_LEVEL)
    log = logging.getLogger(__name__)

    app = Flask(name, static_folder=static_folder)
    app.config.from_object(config)

    is_dev = (
        config.ENV == BackendMode.DEVELOPMENT.value
        or config.ENV == BackendMode.DEVELOPMENT_FULL.value
    )  # noqa: W503

    if is_dev:
        log.warning("RUNNING IN DEVELOPMENT MODE")

    if settings.DISABLE_AUTH and not is_dev:
        raise RuntimeError(
            "APP_DISABLE_AUTH is set to True in a non-development environment. "
            "Authentication cannot be disabled in production."
        )

    # Register all the blueprints
    app.register_blueprint(authn_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(csrf_bp)
    app.register_blueprint(probes_bp)
    app.register_blueprint(serving_bp)
    app.register_blueprint(base_routes_bp)

    if config.METRICS:
        enable_metrics(app)

    @app.after_request
    def set_security_headers(response):
        response.headers["Content-Security-Policy"] = _CSP
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        return response

    return app
