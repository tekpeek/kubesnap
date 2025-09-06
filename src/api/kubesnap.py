from fastapi import FastAPI, HTTPException, Depends, Request
import uvicorn
from fastapi.responses import JSONResponse
import logging
import sys
import time
import datetime
from typing import Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from fastapi.middleware.cors import CORSMiddleware
from kubesnap_functions import create_snapshot
from kubesnap_functions import *
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

#v1 = client.BatchV1Api()
#v1_core = client.CoreV1Api()
#v1_core_apps = client.AppsV1Api()
kubesnap = FastAPI()

# Add CORS middleware
kubesnap.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def api_key_auth(request: Request):
    api_key = request.headers.get('X-API-Key')
    expected_key = os.getenv('SF_API_KEY')
    if not api_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")

@kubesnap.get("/api/kubesnap/health")
def health_check():
    time_stamp = datetime.datetime.now(datetime.UTC)
    return JSONResponse({
            "status": "OK",
            "timestamp": f"{time_stamp}"
    })

@kubesnap.get("/api/kubesnap/{namespace}")
async def create_snapshot_api(#dep=Depends(api_key_auth)
                             namespace) -> Dict[str, Any]:
    try:
        time_string = str(time.time())
        logger.info(f"Triggering Snapshot creation on request at {time_string}")
        zip_file = create_snapshot(namespace)
        logger.info(f"Snapshot created successfully : {zip_file}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Snapshot successfully",
                "file_name": zip_file,
                "timestamp": time_string
            }
        )
        
    except ApiException as e:
        logger.error(f"Failed to create snapshot: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": f"Failed to create snapshot: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": f"Unexpected error: {str(e)}"}
        )


if __name__ == "__main__":
    logger.info("Starting up kubesnap server")
    uvicorn.run("kubesnap:kubesnap", host="0.0.0.0", port=9001, log_level="info")
