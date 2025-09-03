from kubernetes import client, config
import json
import tempfile

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1_core = client.CoreV1Api()
v1_apps = client.AppsV1Api()
v1_batch = client.BatchV1Api()

def fetch_resource_list(api,namespace):
    resource_list = api(namespace).items
    resource_name_array = []
    for resource in resource_list:
        resource_name_array.append(resource.metadata.name)
    return resource_name_array

def fetch_logs(namespace,pod_list,temp_file_path):
    for pod in pod_list:
        logs = v1_core.read_namespaced_pod_log(pod,namespace)
        with open(f"{temp_file_path}/{pod}.log","w") as file:
            file.write(logs)
            print(f"File Created {temp_file_path}/{pod}.log")

# Return list of namespaces
def get_namespaces():
    namespaces_raw=v1_core.list_namespace(_preload_content=False).json()
    namespaces_list=[]
    for namespace_element in namespaces_raw['items']:
        namespaces_list.append(namespace_element['metadata']['name'])

    return namespaces_list

# Return list of pods
def get_pods(namespace):
    return fetch_resource_list(v1_core.list_namespaced_pod,namespace)
    pod_list = v1_core.list_namespaced_pod(namespace).items
    pod_name_array = []
    for pod in pod_list:
        pod_name_array.append(pod.metadata.name)
    return pod_name_array

#print(get_pods("default"))
#fetch_logs("default",get_pods("default"))
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
    temp_file = tempfile.TemporaryDirectory()
    temp_file_path = temp_file.name
    pod_list = get_pods("default")
    fetch_logs("default",pod_list,temp_file_path)
    print(temp_file_path)
    temp_file.cleanup()
    return

create_snapshot("default")
