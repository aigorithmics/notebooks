from flask import request
from kubeflow.kubeflow.crud_backend import api, logging

from ...common import utils, status, viewer as viewer_utils
from . import bp

log = logging.getLogger(__name__)

_DEFAULT_PAGE_SIZE = 50
_MAX_PAGE_SIZE = 500


@bp.route("/api/namespaces/<namespace>/pvcs")
def get_pvcs(namespace):
    try:
        limit = max(
            1, min(int(request.args.get("limit", _DEFAULT_PAGE_SIZE)), _MAX_PAGE_SIZE)
        )
    except (TypeError, ValueError):
        limit = _DEFAULT_PAGE_SIZE
    continue_token = request.args.get("continue") or None

    # Paginated PVC list — controlled by the caller.
    pvcs = api.list_pvcs(namespace, limit=limit, continue_token=continue_token)

    # Notebooks and viewers are fetched fully to guarantee we can
    # form the correct relationships (e.g. which PVCs are mounted to what).
    notebooks = []
    nb_continue = None
    while True:
        nb_page = api.list_notebooks(
            namespace, limit=_MAX_PAGE_SIZE, continue_token=nb_continue
        )
        notebooks.extend(nb_page.get("items", []))
        nb_continue = nb_page.get("metadata", {}).get("continue")
        if not nb_continue:
            break

    pvc_to_notebooks = {}
    for nb in notebooks:
        for vol_pvc_name in utils.get_notebook_pvcs(nb):
            pvc_to_notebooks.setdefault(vol_pvc_name, []).append(nb["metadata"]["name"])

    content = [utils.parse_pvc(pvc, pvc_to_notebooks) for pvc in pvcs.items]

    # Mix-in the viewer status to the response
    viewers = {
        v["metadata"]["name"]: v
        for v in api.list_custom_rsrc(*viewer_utils.VIEWER, namespace)["items"]
    }

    for pvc in content:
        viewer = viewers.get(pvc["name"], {})
        pvc["viewer"] = {
            "status": status.viewer_status(viewer),
            "url": viewer.get("status", {}).get("url", None),
        }

    # V1ListMeta exposes the continue token as _continue (reserved keyword).
    next_continue = pvcs.metadata._continue or None
    remaining = pvcs.metadata.remaining_item_count

    return api.success_response(
        "pvcs",
        content,
        nextContinue=next_continue,
        remainingItemCount=remaining,
    )


@bp.route("/api/namespaces/<namespace>/pvcs/<pvc_name>")
def get_pvc(namespace, pvc_name):
    pvc = api.get_pvc(pvc_name, namespace)
    return api.success_response("pvc", api.serialize(pvc))


@bp.route("/api/namespaces/<namespace>/pvcs/<pvc_name>/pods")
def get_pvc_pods(namespace, pvc_name):
    pods = utils.get_pods_using_pvc(pvc_name, namespace)

    return api.success_response("pods", api.serialize(pods))


@bp.route("/api/namespaces/<namespace>/pvcs/<pvc_name>/events")
def get_pvc_events(namespace, pvc_name):
    events = api.list_pvc_events(namespace, pvc_name).items

    return api.success_response("events", api.serialize(events))
