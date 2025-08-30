from kubernetes import client, config
import json

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1_core = client.CoreV1Api()

# Return list of namespaces
def get_namespaces():
    namespaces_raw=v1_core.list_namespace(_preload_content=False).json()
    namespaces_list=[]
    for namespace_element in namespaces_raw['items']:
        namespaces_list.append(namespace_element['metadata']['name'])

    return namespaces_list

# Return list of pods
def get_pods(namespace):
    pod_list = v1_core.list_namespaced_pod(namespace).items
    pod_name_array = []
    for pod in pod_list:
        pod_name_array.append(pod.metadata.name)
    return pod_name_array

# Return list of deployments


# Return list of configmaps

# Return list of jobs



def create_snapshot(namespace: str):
    return
