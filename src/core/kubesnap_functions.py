from kubernetes import client, config
import json

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1 = client.BatchV1Api()
v1_core = client.CoreV1Api()
v1_core_apps = client.AppsV1Api()
namespaces_raw=v1_core.list_namespace(_preload_content=False).json()
print(namespaces_raw.items())



def create_snapshot(namespace: str):
    return
