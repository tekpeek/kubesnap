from kubernetes import client, config
import json
import tempfile
import subprocess
import logging
import zipfile
import datetime

def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Return a configured logger with console output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)
    return logger

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1_core = client.CoreV1Api()
v1_apps = client.AppsV1Api()
v1_batch = client.BatchV1Api()
logger = get_logger("kubesnap_functions",logging.INFO)

def fetch_resource_list(api,namespace):
    resource_list = api(namespace).items
    resource_name_array = []
    for resource in resource_list:
        resource_name_array.append(resource.metadata.name)
    return resource_name_array

def create_sub_dir(temp_file_path,sub_path):
    try:
        subprocess.run(["mkdir","-p",f"{temp_file_path}/{sub_path}"])
    except Exception as e:
        logger.error(f"Error creating directory {temp_file_path}/{sub_path}: {e}")
        exit(1)

def loop_and_store(element_list,fetch_api,namespace,file_suffix,temp_file_path):
    try:
        for element in element_list:
            config = fetch_api(element,namespace)
            with open(f"{temp_file_path}/{element}.{file_suffix}.txt","w") as file:
                file.write(str(config))
            logger.info(f"File Created {temp_file_path}/{element}.{file_suffix}.txt")
        return
    except Exception as e:
        logger.error(f"Error while creating files for {file_suffix} suffix - api - {fetch_api}")

def zip_files(temp_file_path):
    try:
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
        timestamp = str(timestamp).replace(" ","_")
        timestamp = str(timestamp).replace("\\","_")
        timestamp = str(timestamp).replace("-","_")
        subprocess.run(["zip",f"kubesnap_{timestamp}.zip","-r",f"{temp_file_path}"])
    except Exception as e:
        logger.error(f"Error while creating zip file from folder {temp_file_path}")
    return f"kubesnap_{timestamp}.zip"


def fetch_logs(namespace,temp_file_path):
    pod_list = fetch_resource_list(v1_core.list_namespaced_pod,namespace)
    create_sub_dir(temp_file_path,"pod_logs")
    temp_file_path = temp_file_path + "/pod_logs"
    loop_and_store(pod_list,v1_core.read_namespaced_pod_log,namespace,"log",temp_file_path)

# Return list of namespaces
def namespace_exists(namespace):
    namespaces_raw=v1_core.list_namespace(_preload_content=False).json()
    namespaces_list=[]
    for namespace_element in namespaces_raw['items']:
        namespaces_list.append(namespace_element['metadata']['name'])
    return namespace in namespaces_list

def get_deployments(temp_file_path,namespace):
    create_sub_dir(temp_file_path,"deployments")
    temp_file_path = temp_file_path + "/deployments"
    deploy_list = fetch_resource_list(v1_apps.list_namespaced_deployment,namespace)
    loop_and_store(deploy_list,v1_apps.read_namespaced_deployment,namespace,"dep",temp_file_path)

# Return list of configmaps
def get_configmaps(temp_file_path,namespace):
    create_sub_dir(temp_file_path,"configmaps")
    temp_file_path = temp_file_path + "/configmaps"
    cm_list = fetch_resource_list(v1_core.list_namespaced_config_map,namespace)
    loop_and_store(cm_list,v1_core.read_namespaced_config_map,namespace,"cm",temp_file_path)

# Return list of jobs
def get_jobs(temp_file_path,namespace):
    create_sub_dir(temp_file_path,"jobs")
    temp_file_path = temp_file_path + "/jobs"
    job_list =  fetch_resource_list(v1_batch.list_namespaced_job,namespace)
    loop_and_store(job_list,v1_batch.read_namespaced_job,namespace,"job",temp_file_path)

def get_cronjobs(temp_file_path,namespace):
    create_sub_dir(temp_file_path,"cronjobs")
    temp_file_path = temp_file_path + "/cronjobs"
    cronjob_list =  fetch_resource_list(v1_batch.list_namespaced_cron_job,namespace)
    loop_and_store(cronjob_list,v1_batch.read_namespaced_cron_job,namespace,"cronjob",temp_file_path)

def create_snapshot(namespace: str):
    if not namespace_exists(namespace):
        exit(f"Namespace {namespace} does not exist!")
    temp_file = tempfile.TemporaryDirectory()
    temp_file_path = temp_file.name
    fetch_logs(namespace,temp_file_path)
    get_deployments(temp_file_path,namespace)
    get_jobs(temp_file_path,namespace)
    get_cronjobs(temp_file_path,namespace)
    get_configmaps(temp_file_path,namespace)
    zip_file = zip_files(temp_file_path)
    logger.info(f"Temp Folder Path : temp_file_path")
    logger.info(f"ZIP File Created : {zip_file}")  
    temp_file.cleanup()
    return


create_snapshot("default")
