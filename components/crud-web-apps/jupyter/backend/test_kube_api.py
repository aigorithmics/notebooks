from kubeflow.kubeflow.crud_backend import api, logging
import inspect
from kubernetes import client

print(inspect.signature(client.CustomObjectsApi.list_namespaced_custom_object))
