# Azure Function Main Module
# This module is designed to be run as an Azure Function.
import azure.functions as func
import os
import json
import cv2
import numpy as np
from io import BytesIO
from azure.storage.blob import BlobServiceClient
from core.segment import SegmentIt
from core.correct import correct_image
from core.classify import predict_image
from core.send_signal import send_signal

def score_init():
    global yolo_model_path, classifier_model_path, blob_conn_str
    yolo_model_path = os.getenv("YOLO_MODEL_PATH", "temp_models/yolo.pt")
    classifier_model_path = os.getenv("CLASSIFIER_MODEL_PATH", "temp_models/classifier.pth")
    blob_conn_str = os.getenv("BLOB_CONNECTION_STRING")

def download_image_from_blob(container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(blob_conn_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    stream = blob_client.download_blob()
    image_bytes = BytesIO()
    stream.readinto(image_bytes)
    np_arr = np.frombuffer(image_bytes.getvalue(), np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image

def score_run(container_name, blob_name):
    try:
        image = download_image_from_blob(container_name, blob_name)

        segmenter = SegmentIt(image=image, model_path=yolo_model_path)
        segmenter.run_inference()

        panel = segmenter.get_panel()
        plant_masks = segmenter.generate_masks()

        signal = []
        for i in range(1, 7):
            key = f"plant {i}"
            if key in plant_masks:
                corrected = correct_image(plant_masks[key][0], panel)
                label = predict_image(corrected, model_path=classifier_model_path)
                signal.append(label)
            else:
                signal.append("No plant")

        return {"predictions": signal}
    except Exception as e:
        return {"error": str(e)}

# Azure Function HTTP trigger

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        container_name = req_body.get("container")
        blob_name = req_body.get("image_blob")

        if container_name and blob_name:
            score_init()
            response = score_run(container_name, blob_name)
            return func.HttpResponse(json.dumps(response), status_code=200)

        return func.HttpResponse("Invalid request: must include 'container' and 'image_blob'.", status_code=400)

    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
