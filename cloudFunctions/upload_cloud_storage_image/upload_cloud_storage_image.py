import base64
from google.cloud import storage
import json
import io


def upload_cloud_storage_image(request):

    bucketName = "synthetic-cargo-products"

    # Connect to bucket
    storage_client = storage.Client.from_service_account_json(
        "google-functions-cloud-storage-key.json")
    bucket = storage_client.get_bucket(bucketName)

    imageName = request.form['id'] + ".jpg"
    blob = bucket.blob(imageName)

    image = base64.b64decode(request.form['image'])

    myFile = io.BytesIO(image)

    result = blob.upload_from_file(myFile)

    return "Successfully uploaded image " + imageName
