from kubeflow.kubeflow.crud_backend import api, logging
from flask import request
import json

from ...common import utils, status, viewer as viewer_utils
from . import bp

log = logging.getLogger(__name__)


_CAPACITY_SUFFIXES = {
    'Ei': 1024**6, 'Pi': 1024**5, 'Ti': 1024**4, 'Gi': 1024**3,
    'Mi': 1024**2, 'Ki': 1024,
    'E': 1000**6, 'P': 1000**5, 'T': 1000**4, 'G': 1000**3,
    'M': 1000**2, 'K': 1000, 'k': 1000, 'm': 0.001
}


def _parse_capacity(q):
    if not q:
        return 0
    q = str(q)

    for suffix, multiplier in _CAPACITY_SUFFIXES.items():
        if q.endswith(suffix):
            try:
                return float(q[:-len(suffix)]) * multiplier
            except ValueError:
                return 0

    try:
        return float(q)
    except ValueError:
        return 0


def _get_sort_key(item, sort_by):
    if sort_by == "name":
        return item.get("name", "")
    elif sort_by == "namespace":
        return item.get("namespace", "")
    elif sort_by == "age":
        return item.get("age", "")
    elif sort_by == "capacity":
        return _parse_capacity(item.get("capacity", ""))
    elif sort_by == "status":
        return item.get("status", {}).get("phase", "")
    return ""


@bp.route("/api/namespaces/<namespace>/pvcs")
def get_pvcs(namespace):
    # Return the list of PVCs
    pvcs = api.list_pvcs(namespace)
    notebooks = api.list_notebooks(namespace)["items"]
    content = [utils.parse_pvc(pvc, notebooks) for pvc in pvcs.items]

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

    # 1. Filtering
    filter_by = request.args.get("filterBy", "")
    if filter_by:
        try:
            filters = json.loads(filter_by)
            filtered_contents = []
            for item in content:
                matches_all_tokens = True
                for f in filters:
                    if isinstance(f, str):
                        fq = f.lower()
                        if (fq not in item.get("name", "").lower() and 
                            fq not in item.get("namespace", "").lower() and 
                            fq not in item.get("status", {}).get("phase", "").lower()):
                            matches_all_tokens = False
                            break
                    elif isinstance(f, dict):
                        for k, v in f.items():
                            if k == "namespace" and v not in item.get("namespace", "").lower():
                                matches_all_tokens = False
                            elif k == "name" and v not in item.get("name", "").lower():
                                matches_all_tokens = False
                            elif k == "status" and v not in item.get("status", {}).get("phase", "").lower():
                                matches_all_tokens = False
                        if not matches_all_tokens:
                            break
                if matches_all_tokens:
                    filtered_contents.append(item)
                    
            content = filtered_contents
        except json.JSONDecodeError as e:
            log.warning(f"Failed to parse filterBy: {e}")

    # 2. Sorting
    sort_by = request.args.get("sortBy", "")
    sort_direction = request.args.get("sortDirection", "asc")
    if sort_direction not in ["asc", "desc"]:
        sort_direction = "asc"
    
    if sort_by:
        content.sort(key=lambda item: _get_sort_key(item, sort_by), reverse=(sort_direction == "desc"))
        
    total_count = len(content)

    # 3. Pagination
    limit_str = request.args.get("limit")
    page_str = request.args.get("page")
    
    if limit_str and page_str:
        try:
            limit = int(limit_str)
            page = int(page_str)
            if limit > 0 and page >= 0:
                start = page * limit
                end = start + limit
                content = content[start:end]
        except ValueError:
            pass

    return api.success_response("pvcs", content, totalCount=total_count)


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
