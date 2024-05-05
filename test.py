from ToolGPT import ChatGPTWithFunctions

import os
import ollama
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

load_dotenv()

# openai.api_key = "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"

# client = ollama.Client(os.getenv("OLLAMA_API_KEY"))

prompt = "Add me 4 units of 'CALIERCORTIN' to my list"
wrapper = ChatGPTWithFunctions()
order_list = []


import json
import pandas as pd
from typing import List

def add_product_to_order_list(name: str) -> str:
    """
    Add a product to the order list.
    
    Parameters
    ----------
    name : str
        The name of the product to add.

    Returns
    -------
    str
        The response message.
    """
    # Add a product to the order list
    product = search_product(name)

    if product is None:
        return "Product not found"

    order_list.append(product)

    return "Product added to order list"


def product_list() -> str:
    """
    Get the list of products.
    
    Parameters
    ----------
    None

    Returns
    -------
    str
        The list of products as a string.
    """

    df = pd.read_csv("/home/brunomoya/development/hackupc/seidor-hackupc/api/app/services/products.csv", delimiter=";")
    product_descriptions = []

    try:
        response = df.to_json(orient="records")
        for item in json.loads(response):
            print(item)
            product_descriptions.append(f"ID: {item['id']}, Name: {item['name']}, EAN: {item['ean']}")
    except ValueError as e:
        return f"Error parsing JSON: {e}\nResponse text: {response.text}"

    result_string = ', '.join(product_descriptions)

    return result_string

def my_list() -> str:
    """
    Get the current order list.
    
    Parameters
    ----------
    None

    Returns
    -------
    str
    """

    # return the current order list as a string
    string_list = [f"ID: {item['id']}, Name: {item['name']}, EAN: {item['ean']}" for item in order_list]
    print(string_list)
    return string_list


def search_product(product_name: str) -> dict:
    """
    Search for a product in the list of products.

    Args:
        product_name (str): The name of the product to search for.

    Returns:
        dict: The product information if found, None otherwise.
    """

    df = pd.read_csv("/home/brunomoya/development/hackupc/seidor-hackupc/api/app/services/products.csv", delimiter=";")
    product = df[df["name"].str.contains(product_name, case=False, na=False)].to_dict(orient="records")
    if len(product) > 0:
        return product[0]
    else:
        return None

def similarity(user_input_name: str, product_name: str) -> float:
    """
    Check the similarity between two strings.

    Args:
        user_input_name (str): The user input string.
        product_name (str): The product name string.

    Returns:
        float: The similarity score between the two strings.
    """
    # Check the similarity between two strings
    return fuzz.token_sort_ratio(user_input_name, product_name)


def remove_product_from_order_list(id: str) -> List[dict]:
    """
    Remove a product from the order list.

    Args:
        id (str): The id of the product to remove.

    Returns:
        List[dict]: The updated order list.
    """
    # Remove a product from the order list
    order_list = [item for item in order_list if item["id"] != id]
    return order_list

def save_order_list() -> None:
    """
    Save the order list to a file.

    """
    # Save the order list to a file
    with open("order_list.txt", "w") as f:
        for item in order_list:
            f.write("%s\n" % item)



ans = wrapper.prompt_with_functions(prompt, [add_product_to_order_list, product_list, my_list])
print(ans)