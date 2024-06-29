import os

import requests
from dotenv import load_dotenv


class QuantityUpdater:
    def update_quantity(self, inventory_item_id, available_amount):
        print('update quantity', inventory_item_id)
        self.shopify_store_url = 'https://7c70bf.myshopify.com/admin/api/2023-10/inventory_levels/set.json'
        load_dotenv()
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.shop_location_id = 89627787602
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": self.access_token}
        payload = {"location_id": self.shop_location_id, "inventory_item_id": inventory_item_id,
                   "available": available_amount}
        response = requests.post(url=self.shopify_store_url, headers=headers, json=payload)
        if response.status_code == 200:
            return True
        else:
            return False

