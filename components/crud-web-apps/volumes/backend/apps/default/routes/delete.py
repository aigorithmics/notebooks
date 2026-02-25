from werkzeug import exceptions

from kubeflow.kubeflow.crud_backend import api, logging

from ...common import utils as common_utils
from ...common import viewer as viewer_utils
from . import bp

log = logging.getLogger(__name__)


@bp.route("/api/namespaces/<namespace>/pvcs/<pvc>", methods=["DELETE"])
def delete_pvc(pvc, namespace):
    """
    Delete a PVC.
    Kubernetes natively uses the 'pvc-protection' finalizer to prevent
    deletion if the PVC is actively mounted to a running Pod. We rely
    on this instead of manually querying and looping all Pods in the namespace.
    """

    # Check if a viewer custom resource is attached to this PVC and delete it
    viewer_name = f"{pvc}-viewer"
    try:
        viewer = api.get_custom_rsrc(*viewer_utils.VIEWER, viewer_name, namespace)
        if viewer:
            delete_viewer(viewer_name, namespace)
    except exceptions.NotFound:
        pass
    except Exception as e:
        log.warning("Failed to check for viewer %s: %s", viewer_name, e)

    log.info("Deleting PVC %s/%s...", namespace, pvc)
    api.delete_pvc(pvc, namespace)
    log.info("Successfully initiated deletion for PVC %s/%s", namespace, pvc)

    return api.success_response("message", "PVC %s successfully deleted." % pvc)


@bp.route("/api/namespaces/<namespace>/viewers/<viewer>", methods=["DELETE"])
def delete_viewer(viewer, namespace):
    """
    Delete a viewer.
    """
    log.info("Deleting viewer %s/%s...", namespace, viewer)
    api.delete_custom_rsrc(*viewer_utils.VIEWER, viewer, namespace)
    log.info("Successfully deleted viewer %s/%s", namespace, viewer)

    return api.success_response("message", "Viewer %s successfully deleted." % viewer)
