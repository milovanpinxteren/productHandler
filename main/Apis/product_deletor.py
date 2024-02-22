import os

import requests
from dotenv import load_dotenv


class ProductDeletor:
    def delete_product(self, productID):
        print('delete product')
        self.shopify_store_url = f'https://7c70bf.myshopify.com/admin/api/2023-10/products/{productID}.json'
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        response = requests.delete(url=self.shopify_store_url, headers=headers)
