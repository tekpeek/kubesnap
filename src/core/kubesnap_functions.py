from kubernetes import client, config
import json

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1_core = client.CoreV1Api()
v1_apps = client.AppsV1Api()
v1_batch = client.BatchV1Api()

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
def get_deployments(namespace):
    deploy_list = v1_apps.list_namespaced_deployment(namespace).items
    deploy_name_array = []
    for deploy in deploy_list:
        deploy_name_array.append(deploy.metadata.name)
    return deploy_name_array

# Return list of configmaps
def get_configmaps(namespace):
    cm_list = v1_core.list_namespaced_config_map(namespace).items
    cm_name_array = []
    for cm in cm_list:
        cm_name_array.append(cm.metadata.name)
    return cm_name_array

# Return list of jobs
def get_jobs(namespace):
    job_list = v1_batch.list_namespaced_job(namespace).items
    job_name_array = []
    for job in job_list:
        job_name_array.append(job.metadata.name)
    return job_name_array

def get_cronjobs(namespace):
    cronjob_list = v1_batch.list_namespaced_cron_job(namespace).items
    cronjob_name_array = []
    for cronjob in cronjob_list:
        cronjob_name_array.append(cronjob.metadata.name)
    return cronjob_name_array

def create_snapshot(namespace: str):
    return
