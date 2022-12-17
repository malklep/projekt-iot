import os

import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse("ERROR", status_code=500)

        registry_manager = IoTHubRegistryManager(os.environ["ConnectionString"])
        for device in filter(lambda d: d["errors"] > 3, req_body):
            registry_manager.invoke_device_method(
                device_id=device["ConnectionDeviceId"],
                direct_method_request=CloudToDeviceMethod(method_name="emergency_stop")
            )
        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
