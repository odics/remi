from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import shutil
import json
import isodate
import re


# Recipe class that will be returned, which will contain all the necessary information for each recipe parses from
# the URL:
class Recipe:
    def __init__(self, title, prep, cook, rest, total, servings, ingredients, instructions, image, ingredient_list):
        self.title = title
        self.prep = prep
        self.cook = cook
        self.rest = rest
        self.total = total
        self.servings = servings
        self.ingredients = ingredients
        self.instructions = instructions
        self.image = image
        self.ingredient_list = ingredient_list


# Function to download and store recipe images. Essentially copy/pasted from
# https://www.scrapingbee.com/blog/download-image-python/
def download_image(url, file_name):
    res = requests.get(url, stream=True)
    file_name = "./website/static/" + file_name

    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
    else:
        print('Image Couldn\'t be retrieved')


# Convert ISO8601 time duration to human readable time. Big thanks to StackOverflow for providing the isodate solution.
def get_time(iso_time):
    parsed_time = isodate.parse_duration(iso_time)
    parsed_time_list = str(parsed_time).split(":")

    if parsed_time_list[0] != "0":
        parsed_time = parsed_time_list[0] + " hours and " + parsed_time_list[1] + " minutes"
        return parsed_time
    else:
        parsed_time = parsed_time_list[1] + " minutes"
        return parsed_time


def recipe_parser(url):
    # Parse URL into components for later checking of which website the recipe is from:
    parsed_url = urlparse(url)

    result = requests.get(url)
    doc = BeautifulSoup(result.text, features="html.parser")

    recipe_details = doc.find(type="application/ld+json")
    recipe_json = json.loads(recipe_details.text)

    # Store a single variable of ingredients with HTML formatting. The URL check is needed because woksoflife structures
    # its JSON in a very weird way.
    joined_ingredients = ""
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        for ingredient in recipe_json['@graph'][7].get('recipeIngredient'):
            joined_ingredients += "<li>" + ingredient + "</li><br>"
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "recipeIngredient" in json_key.keys():
                    for ingredient in json_key.get('recipeIngredient'):
                        joined_ingredients += "<li>" + ingredient + "</li><br>"
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "recipeIngredient" in item.keys():
                if isinstance(item.get('recipeIngredient'), list):
                    for ingredient in item.get('recipeIngredient'):
                        joined_ingredients += "<li>" + ingredient + "</li><br>"
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        for ingredient in recipe_json['@graph'][7].get('recipeIngredient'):
            joined_ingredients += "<li>" + ingredient + "</li><br>"
    else:
        for ingredient in recipe_json[0].get('recipeIngredient'):
            joined_ingredients += "<li>" + ingredient + "</li><br>"

    # Store a single variable of instructions with HTML formatting. Same URL check as above:
    joined_instructions = ""
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        for instruction in recipe_json['@graph'][7].get('recipeInstructions'):
            joined_instructions += "<li>" + instruction['text'] + "</li><br>"
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "recipeInstructions" in json_key.keys():
                    for instruction in json_key.get('recipeInstructions'):
                        joined_instructions += "<li>" + instruction['text'] + "</li><br>"
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "recipeInstructions" in item.keys():
                if isinstance(item.get('recipeInstructions'), list):
                    for instruction in item.get('recipeIngredient'):
                        joined_instructions += "<li>" + instruction + "</li><br>"
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        for instruction in recipe_json['@graph'][7].get('recipeInstructions'):
            joined_instructions += "<li>" + instruction['text'] + "</li><br>"
    else:
        for instruction in recipe_json[0].get('recipeInstructions'):
            joined_instructions += "<li>" + instruction['text'] + "</li><br>"

    # Python lists of instructions and ingredients. Again, URL checking:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        ingredient_list = recipe_json['@graph'][7].get('recipeIngredient')
        instruction_list = recipe_json['@graph'][7].get('recipeInstructions')
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "recipeInstructions" in json_key.keys():
                    ingredient_list = json_key.get('recipeInstructions')
                    instruction_list = json_key.get('recipeInstructions')
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "recipeInstructions" in item.keys():
                if isinstance(item.get('recipeInstructions'), list):
                    ingredient_list = item.get('recipeInstructions')
                    instruction_list = item.get('recipeInstructions')
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        ingredient_list = recipe_json['@graph'][7].get('recipeIngredient')
        instruction_list = recipe_json['@graph'][7].get('recipeInstructions')
    else:
        ingredient_list = recipe_json[0].get('recipeIngredient')
        instruction_list = recipe_json[0].get('recipeInstructions')

    # Parse the ISO8601 time into human readable time:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        cook_time = get_time(recipe_json['@graph'][7]['cookTime'])
        prep_time = get_time(recipe_json['@graph'][7]['prepTime'])
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "cookTime" in json_key.keys():
                    cook_time = get_time(json_key.get('cookTime'))
                if "prepTime" in json_key.keys():
                    prep_time = get_time(json_key.get('prepTime'))
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "prepTime" in item.keys():
                prep_time = get_time(item.get('prepTime'))
            if isinstance(item, dict) and "cookTime" in item.keys():
                cook_time = get_time(item.get('cookTime'))
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        cook_time = get_time(recipe_json['@graph'][7]['cookTime'])
        prep_time = get_time(recipe_json['@graph'][7]['prepTime'])
    else:
        cook_time = get_time(recipe_json[0]['cookTime'])
        prep_time = get_time(recipe_json[0]['prepTime'])

    # Check to see if recipe has a rest time. If not, set rest time to 0 minutes:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        rest_time = get_time(recipe_json['@graph'][7].get('restTime', 'PT0M'))
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "restTime" in json_key.keys():
                    rest_time = get_time(json_key.get('restTime', "PT0M"))
                else:
                    rest_time = "PT0M"
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "restTime" in item.keys():
                rest_time = get_time(item.get('restTime'))
            else:
                rest_time = "PT0M"
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        rest_time = get_time(recipe_json['@graph'][7].get('restTime', 'PT0M'))
    else:
        rest_time = get_time(recipe_json[0].get('restTime', 'PT0M'))

    if "thewoksoflife" in str(parsed_url.netloc).lower():
        total_time = get_time(recipe_json['@graph'][7]['totalTime'])
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "totalTime" in json_key.keys():
                    total_time = get_time(json_key.get('totalTime'))
                    break
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "totalTime" in item.keys():
                total_time = get_time(item.get('totalTime'))
                break
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        total_time = get_time(recipe_json['@graph'][7]['totalTime'])
    else:
        total_time = get_time(recipe_json[0]['totalTime'])

    # Get the recipe title:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        recipe_title = recipe_json['@graph'][7]['name']
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "name" in json_key.keys():
                    recipe_title = json_key.get('name')
                    break
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "name" in item.keys():
                recipe_title = item.get('name')
                break
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        recipe_title = recipe_json['@graph'][7]['name']
    else:
        recipe_title = recipe_json[0]['headline']

    # Get the amount of servings based on website. Allrecipes returns a weird value, so it has to be cleaned up. Also
    # some websites contain this value in a list. If that's the case, we generally only want the first item of the list.
    if "allrecipes" in str(parsed_url.netloc).lower():
        total_servings = re.sub('[^A-Za-z0-9]+', '', str(recipe_json[0]['recipeYield']))
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "recipeYield" in json_key.keys():
                    total_servings = json_key.get('recipeYield')
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "recipeYield" in item.keys():
                total_servings = item.get('recipeYield')
            else:
                rest_time = "PT0M"
    elif "thewoksoflife" in str(parsed_url.netloc).lower():
        total_servings = str(recipe_json['@graph'][7]['recipeYield'][0])
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        total_servings = str(recipe_json['@graph'][7]['recipeYield'][0])
    elif type(recipe_json[0]['recipeYield']) == list:
        total_servings = recipe_json[0]['recipeYield'][0]
    else:
        total_servings = str(recipe_json[0]['recipeYield'])

    # Get the URL for the recipe image, create the image filename, and download the image:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        image_url = recipe_json['@graph'][7]['image'][0]
    elif isinstance(recipe_json, dict):
        if recipe_json['@graph']:
            for json_key in recipe_json['@graph']:
                if "image" in json_key.keys():
                    image_url = json_key.get('image')
                    if isinstance(image_url, dict):
                        image_url = list(image_url.values())[0]
                        break
    elif isinstance(recipe_json, list):
        for item in recipe_json:
            if isinstance(item, dict) and "image" in item.keys():
                if isinstance(item.get('image'), dict):
                    image_url = item.get('image').get('url')
                else:
                    image_url = item.get('image')
    elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
        image_url = recipe_json['@graph'][7]['image'][0]
    else:
        image_url = recipe_json[0]['image']['url']

    image_title = recipe_title.strip()
    image_title = re.sub('[^A-Za-z0-9]+', '', image_title) + ".jpg"

    download_image(image_url, image_title)

    recipe_data = Recipe(recipe_title, prep_time, cook_time, rest_time,
                         total_time, total_servings, joined_ingredients, joined_instructions, image_title,
                         ingredient_list)

    return recipe_data


recipe_parser("https://www.simplyrecipes.com/tex-mex-chopped-chicken-salad-with-cilantro-lime-dressing-5179994")
# recipe_parser("https://tastesbetterfromscratch.com/bread-recipe/")