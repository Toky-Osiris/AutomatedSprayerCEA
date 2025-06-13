from azure.iot.hub import IoTHubRegistryManager
import json


CONNECTION_STRING = "Enter connection string"
DEVICE_ID = "Enter esp32 device id"

def send_signal_to_esp32(solenoids, duration_ms=18000):
    signal = {
        "solenoids": solenoids,
        "duration": duration_ms
    }
    message_json = json.dumps(signal)

    try:
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)
        registry_manager.send_c2d_message(DEVICE_ID, message_json)
        print(f"[INFO] Message sent to device '{DEVICE_ID}': {message_json}")
    except Exception as e:
        print("[ERROR]", e)
 
