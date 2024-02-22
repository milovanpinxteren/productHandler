import os

import requests
import base64
from io import BytesIO

from dotenv import load_dotenv


class ImageUploader:
    def __init__(self):
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }

    def image_to_base64(self, image):
        """ Convert PIL Image to base64-encoded string """
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def upload_image_to_shopify(self, productID, image):
        self.shopify_store_url = f'https://7c70bf.myshopify.com/admin/api/2023-10/products/{productID}/images.json'
        self.headers = {"Accept": "application/json", "Content-Type": "application/json",
                        "X-Shopify-Access-Token": self.access_token}
        encoded_image = self.image_to_base64(image)
        payload = {"image": {"attachment": encoded_image}}
        response = requests.post(url=self.shopify_store_url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return True, response.status_code
        else:
            return False, response.status_code
