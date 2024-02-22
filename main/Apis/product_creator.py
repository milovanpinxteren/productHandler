import requests
from dotenv import load_dotenv
import os

class ProductCreator:
    def create_product_on_shopify(self, data):
        print('create product')
        self.shopify_store_url = 'https://7c70bf.myshopify.com/admin/api/2023-10/products.json'
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        payload = {"product": data}
        response = requests.post(url=self.shopify_store_url, headers=headers, json=payload)

        if response.status_code == 201:
            productID = response.json()['product']['id']
            variantID = response.json()['product']['variants'][0]['id']
            inventory_item_id = response.json()['product']['variants'][0]['inventory_item_id']
            return productID, variantID, inventory_item_id
        else:
            print('failed', response.status_code)
            return None
