import requests
from dotenv import load_dotenv
import os
import re
class ProductCreator:

    def create_product_on_shopify(self, data, btw_tag):
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
                self.publish_product_to_all_channels(response_data['data']['productCreate']['product']['id'])
                if btw_tag == 'BTW Hoog':
                    collection_id = "gid://shopify/Collection/637676978514"
                elif btw_tag == 'BTW Laag':
                    collection_id = "gid://shopify/Collection/637677764946"
                if btw_tag == 'BTW 0':
                    collection_id = "gid://shopify/Collection/637677797714"
                self.add_product_to_collection(collection_id, response_data['data']['productCreate']['product']['id'])
                return productID, variantID, inventory_item_id
        else:
            print('failed', response.status_code)
            return None

    def add_product_to_collection(self, collection_id, product_id):
        query = """
        mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
            collectionAddProducts(id: $id, productIds: $productIds) {
                collection {
                    id
                    title
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        # Variables for the mutation
        variables = {
            "id": collection_id,
            "productIds": [product_id]
        }

        try:
            # Execute the query using the provided function
            response_data = self.execute_graphql_query(query, variables)

            # Handle the response
            if "errors" in response_data:
                print("Errors:", response_data["errors"])
            elif response_data.get("data", {}).get("collectionAddProducts", {}).get("userErrors"):
                print("User Errors:", response_data["data"]["collectionAddProducts"]["userErrors"])
            else:
                collection = response_data["data"]["collectionAddProducts"]["collection"]
                print(f"Product added to collection: {collection['title']} (ID: {collection['id']})")
        except Exception as e:
            print(f"An error occurred: {e}")

    def publish_product_to_all_channels(self, product_id):
        """
        Publishes a product to all hardcoded sales channels.
        """
        PUBLICATIONS = [
            {'node': {'id': 'gid://shopify/Publication/188717662546', 'name': 'Online Store'}},
            {'node': {'id': 'gid://shopify/Publication/188717695314', 'name': 'Point of Sale'}},
            {'node': {'id': 'gid://shopify/Publication/188717760850', 'name': 'Shop'}},
            {'node': {'id': 'gid://shopify/Publication/197279678802', 'name': 'Inbox'}},
            {'node': {'id': 'gid://shopify/Publication/197467734354', 'name': 'Google & YouTube'}},
            {'node': {'id': 'gid://shopify/Publication/197766807890', 'name': 'Facebook & Instagram'}},
        ]
        
        for publication in PUBLICATIONS:
            publication_id = publication['node']['id']
            publication_name = publication['node']['name']
            # print(f"Publishing to {publication_name} (ID: {publication_id})")
    
            mutation = """
                mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
                  publishablePublish(id: $id, input: $input) {
                    shop {
                      publicationCount
                    }
                    userErrors {
                      field
                      message
                    }
                  }
                }
            """
            variables = {
                "id": product_id,
                "input": {"publicationId": publication_id}
            }
            response = self.execute_graphql_query(mutation, variables)
            if response.get('errors'):
                print(f"Errors: {response['errors']}")
            elif response['data']['publishablePublish']['userErrors']:
                print(f"User Errors: {response['data']['publishablePublish']['userErrors']}")
            else:
                print(f"Product {product_id} published to {publication_name} successfully.")

    def execute_graphql_query(self, query, variables=None):
        """
        Executes a GraphQL query or mutation against the Shopify API.
        """
        access_token = os.environ["ACCESS_TOKEN"]
        shopify_store_url = 'https://7c70bf.myshopify.com/admin/api/2023-10/graphql.json'
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }

        response = requests.post(
            shopify_store_url,
            json={"query": query, "variables": variables or {}},
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"GraphQL query failed with status code {response.status_code}: {response.text}")