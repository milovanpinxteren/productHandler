import requests
from dotenv import load_dotenv
import os
import re
class ProductCreator:

    def create_product_on_shopify(self, data):
        print('create product')
        load_dotenv()
        access_token = os.environ["ACCESS_TOKEN"]
        shopify_store_url = 'https://7c70bf.myshopify.com/admin/api/2023-10/graphql.json'
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }

        mutation = """
        mutation createProduct($input: ProductInput!) {
            productCreate(input: $input) {
                product {
                    id
                    variants(first: 1) {
                        edges {
                            node {
                                id
                                inventoryItem {
                                    id
                                }
                            }
                        }
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """

        # Prepare the input data
        product_input = {
            "input": {
                "title": data['title'],
                "bodyHtml": data['body_html'],
                "published": True,
                "tags": data['tags'],
                "seo": {
                    "description": data['seo']['description'],
                    "title": data['seo']['title']
                },
                "variants": [{
                    "barcode": data['variants'][0]['barcode'],
                    "price": data['variants'][0]['price'],
                    "weight": data['variants'][0]['grams'],
                    "weightUnit": "GRAMS",
                    "inventoryManagement": data['variants'][0]['inventory_management'],
                    "taxable": data['variants'][0]['taxable']
                }],
                "metafields": [
                    {
                        "namespace": field['namespace'],
                        "key": field['key'],
                        "value": field['value'],
                        "type": field['type']
                    } for field in data['metafields']
                ]
            }
        }

        payload = {
            "query": mutation,
            "variables": product_input
        }
        response = requests.post(url=shopify_store_url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if 'errors' in response_data:
                print('GraphQL errors:', response_data['errors'])
                return None
            else:
                product = response_data['data']['productCreate']['product']
                productID = re.sub(r'\D', '', product['id'])
                variant = product['variants']['edges'][0]['node']
                variantID = re.sub(r'\D', '', variant['id'])
                inventory_item_id = re.sub(r'\D', '', variant['inventoryItem']['id'])
                return productID, variantID, inventory_item_id
        else:
            print('failed', response.status_code)
            return None
