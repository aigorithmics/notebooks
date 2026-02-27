"""GET request handlers."""

from kubeflow.kubeflow.crud_backend import api, logging
from werkzeug.exceptions import NotFound
from flask import request
from typing import Any, Dict, List
import json

from .. import utils
from .. import status
from . import bp

log = logging.getLogger(__name__)


@bp.route("/api/config")
def get_config():
    config = utils.load_spawner_ui_config()
    return api.success_response("config", config)


@bp.route("/api/namespaces/<namespace>/pvcs")
def get_pvcs(namespace):
    pvcs = api.list_pvcs(namespace).items
    data = [
        {
            "name": pvc.metadata.name,
            "size": pvc.spec.resources.requests["storage"],
            "mode": pvc.spec.access_modes[0],
        }
        for pvc in pvcs
    ]

    return api.success_response("pvcs", data)


@bp.route("/api/namespaces/<namespace>/poddefaults")
def get_poddefaults(namespace):
    pod_defaults = api.list_poddefaults(namespace)

    # Return a list of pod defaults adding custom fields (label, desc) for
    # forms
    contents = []
    for pd in pod_defaults["items"]:
        label = list(pd["spec"]["selector"]["matchLabels"].keys())[0]
        if "desc" in pd["spec"]:
            desc = pd["spec"]["desc"]
        else:
            desc = pd["metadata"]["name"]

        pd["label"] = label
        pd["desc"] = desc
        contents.append(pd)

    log.info("Found poddefaults: %s", contents)

    return api.success_response("poddefaults", contents)


@bp.route("/api/namespaces/<namespace>/notebooks")
def get_notebooks(namespace):
    # Note: This implementation fetches all notebooks from Kubernetes and then
    # performs filtering, sorting, and pagination in-memory. While this isn't true
    # "server-side pagination" (which would use Kubernetes API limit/continue), 
    # it is necessary because the Kubernetes API doesn't support server-side
    # sorting and arbitrary property filtering out of the box.
    notebooks = api.list_notebooks(namespace)["items"]
    contents: List[Dict[str, Any]] = [utils.notebook_dict_from_k8s_obj(nb) for nb in notebooks]
    
    # Apply status processing early so we can sort/filter by it
    for notebook in contents:
        notebook["processed_status"] = status.process_status(notebook)

    # 1. Filtering
    filter_by = request.args.get("filterBy", "")
    if filter_by:
        try:
            filters = json.loads(filter_by)
            filtered_contents: List[Dict[str, Any]] = []
            for item in contents:
                matches_all_tokens = True
                for f in filters:
                    if isinstance(f, str):
                        fq = f.lower()
                        if (fq not in item.get("name", "").lower() and 
                            fq not in item.get("namespace", "").lower() and 
                            fq not in item.get("processed_status", {}).get("phase", "").lower()):
                            matches_all_tokens = False
                            break
                    elif isinstance(f, dict):
                        for k, v in f.items():
                            if k == "namespace" and v not in item.get("namespace", "").lower():
                                matches_all_tokens = False
                            elif k == "name" and v not in item.get("name", "").lower():
                                matches_all_tokens = False
                            elif k == "status" and v not in item.get("processed_status", {}).get("phase", "").lower():
                                matches_all_tokens = False
                        if not matches_all_tokens:
                            break
                if matches_all_tokens:
                    filtered_contents.append(item)
                    
            contents = filtered_contents
        except Exception as e:
            log.warning(f"Failed to parse filterBy: {e}")
            pass

    # 2. Sorting
    sort_by = request.args.get("sortBy", "")
    sort_direction = request.args.get("sortDirection", "asc")
    if not sort_direction:
        sort_direction = "asc"
    
    if sort_by:
        def get_sort_key(item):
            if sort_by == "name": return item.get("name", "")
            if sort_by == "namespace": return item.get("namespace", "")
            if sort_by == "age": return item.get("age", "")
            if sort_by == "image": return item.get("image", "")
            if sort_by == "status": return item.get("processed_status", {}).get("phase", "")
            return ""
            
        contents.sort(key=get_sort_key, reverse=(sort_direction == "desc"))
        
    total_count = len(contents)

    # 3. Pagination
    limit_str = request.args.get("limit")
    page_str = request.args.get("page")
    
    if limit_str and page_str:
        try:
            limit = int(limit_str)
            page = int(page_str)
            start = page * limit
            end = start + limit
            contents = [contents[i] for i in range(start, min(end, len(contents)))]
        except ValueError:
            pass

    # Clean up processed_status
    for item in contents:
        item.pop("processed_status", None)

    return api.success_response("notebooks", contents, totalCount=total_count)


@bp.route("/api/namespaces/<namespace>/notebooks/<name>")
def get_notebook(name, namespace):
    notebook = api.get_notebook(name, namespace)
    notebook["processed_status"] = status.process_status(notebook)

    return api.success_response("notebook", notebook)


@bp.route("/api/namespaces/<namespace>/notebooks/<notebook_name>/pod")
def get_notebook_pod(notebook_name, namespace):
    label_selector = "notebook-name=" + notebook_name
    # There should be only one Pod for each Notebook,
    # so we expect items to have length = 1
    pods = api.list_pods(namespace=namespace, label_selector=label_selector)
    if pods.items:
        pod = pods.items[0]
        return api.success_response(
            "pod",
            api.serialize(pod),
        )
    else:
        raise NotFound("No pod detected.")


@bp.route("/api/namespaces/<namespace>/notebooks/<notebook_name>/pod/<pod_name>/logs")  # noqa: E501
def get_pod_logs(namespace, notebook_name, pod_name):
    container = notebook_name
    logs = api.get_pod_logs(namespace, pod_name, container)
    return api.success_response(
        "logs",
        logs.split("\n"),
    )


@bp.route("/api/namespaces/<namespace>/notebooks/<notebook_name>/events")
def get_notebook_events(notebook_name, namespace):
    events = api.list_notebook_events(notebook_name, namespace).items

    return api.success_response(
        "events",
        api.serialize(events),
    )


@bp.route("/api/gpus")
def get_gpu_vendors():
    """
    Return a list of GPU vendors for which at least one node has the necessary
    annotation required to schedule pods
    """
    frontend_config = utils.load_spawner_ui_config()
    gpus_value = frontend_config.get("gpus", {}).get("value", {})
    config_vendor_keys = [v.get("limitsKey", "") for v in gpus_value.get("vendors", [])]

    # Get all of the different resources installed in all nodes
    installed_resources = set()
    nodes = api.list_nodes().items
    for node in nodes:
        if node.status.capacity:
            installed_resources.update(node.status.capacity.keys())
        else:
            log.debug(f"Capacity was not available for node {node.metadata.name}")

    # Keep the vendors the key of which exists in at least one node
    available_vendors = installed_resources.intersection(config_vendor_keys)

    return api.success_response("vendors", list(available_vendors))
