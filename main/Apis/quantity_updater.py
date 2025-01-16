import os

import requests
from dotenv import load_dotenv


class QuantityUpdater:
    def update_quantity_old(self, inventory_item_id, available_amount):
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


    def update_quantity(self, inventory_item_id, available_amount):
        print('Updating quantity for inventory item:', inventory_item_id)
        load_dotenv()
        available_amount = int(available_amount)
        self.access_token = os.environ["ACCESS_TOKEN"]
        self.shopify_graphql_url = 'https://7c70bf.myshopify.com/admin/api/2024-10/graphql.json'
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }
        # GraphQL mutation for setting inventory quantities
        query = """
        mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
            inventorySetQuantities(input: $input) {
                inventoryAdjustmentGroup {
                    createdAt
                    reason
                    changes {
                        name
                        delta
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """

        # Construct the input payload
        location_id = "gid://shopify/Location/89627787602"  # Hardcoded location ID
        quantities_input = {
            "inventoryItemId": f"gid://shopify/InventoryItem/{inventory_item_id}",
            "locationId": location_id,
            "quantity": available_amount
        }

        variables = {
            "input": {
                "name": "available",
                "reason": "correction",
                "ignoreCompareQuantity": True,
                "quantities": [quantities_input]
            }
        }

        payload = {
            "query": query,
            "variables": variables
        }

        response = requests.post(
            url=self.shopify_graphql_url,
            headers=self.headers,
            json=payload
        )

        if response.status_code == 200:
            response_data = response.json()
            errors = response_data.get("data", {}).get("inventorySetQuantities", {}).get("userErrors", [])
            if not errors:
                print("Quantity updated successfully.")
                return True
            else:
                print("GraphQL errors:", errors)
                return False
        else:
            print("Request failed with status code:", response.status_code)
            print("Response:", response.text)
            return False