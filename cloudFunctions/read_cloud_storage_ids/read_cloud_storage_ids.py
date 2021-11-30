from google.cloud import storage
from bson.json_util import dumps


def read_cloud_storage_ids(request):

    bucketName = "synthetic-cargo-products"

    # Connect to bucket
    storage_client = storage.Client.from_service_account_json(
        "google-functions-cloud-storage-key.json")
    bucket = storage_client.get_bucket(bucketName)

    blobs = bucket.list_blobs()

    blobIds = []
    for blob in blobs:
        blobIds.append(blob.name)

    json_data = dumps(blobIds)

    return json_data
