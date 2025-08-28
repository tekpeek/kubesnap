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

# Return list of deployments

# Return list of configmaps

# Return list of jobs



def create_snapshot(namespace: str):
    return
