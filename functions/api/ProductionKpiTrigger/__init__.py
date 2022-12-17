import os

import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse("ERROR", status_code=500)

        registry_manager = IoTHubRegistryManager(os.environ["ConnectionString"])
        for device in filter(lambda d: float(d["kpi"]) < 90, req_body):
            twin = registry_manager.get_twin(device["ConnectionDeviceId"])
            twin.properties.desired["production_rate"] = twin.properties.reported["production_rate"] - 10
            registry_manager.update_twin(device["ConnectionDeviceId"], twin, twin.etag)
        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
