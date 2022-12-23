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
    else:
        for ingredient in recipe_json[0].get('recipeIngredient'):
            joined_ingredients += "<li>" + ingredient + "</li><br>"

    # Store a single variable of instructions with HTML formatting. Same URL check as above:
    joined_instructions = ""
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        for instruction in recipe_json['@graph'][7].get('recipeInstructions'):
            joined_instructions += "<li>" + instruction['text'] + "</li><br>"
    else:
        for instruction in recipe_json[0].get('recipeInstructions'):
            joined_instructions += "<li>" + instruction['text'] + "</li><br>"

    # Python lists of instructions and ingredients. Again, URL checking:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        ingredient_list = recipe_json['@graph'][7].get('recipeIngredient')
        instruction_list = recipe_json['@graph'][7].get('recipeInstructions')
    else:
        ingredient_list = recipe_json[0].get('recipeIngredient')
        instruction_list = recipe_json[0].get('recipeInstructions')

    # Parse the ISO8601 time into human readable time:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        cook_time = get_time(recipe_json['@graph'][7]['cookTime'])
        prep_time = get_time(recipe_json['@graph'][7]['prepTime'])
    else:
        cook_time = get_time(recipe_json[0]['cookTime'])
        prep_time = get_time(recipe_json[0]['prepTime'])

    # Check to see if recipe has a rest time. If not, set rest time to 0 minutes:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        rest_time = get_time(recipe_json['@graph'][7].get('restTime', 'PT0M'))
    else:
        rest_time = get_time(recipe_json[0].get('restTime', 'PT0M'))

    if "thewoksoflife" in str(parsed_url.netloc).lower():
        total_time = get_time(recipe_json['@graph'][7]['totalTime'])
    else:
        total_time = get_time(recipe_json[0]['totalTime'])

    # Get the recipe title:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
        recipe_title = recipe_json['@graph'][7]['name']
    else:
        recipe_title = recipe_json[0]['headline']

    # Get the amount of servings based on website. Allrecipes returns a weird value, so it has to be cleaned up. Also
    # some websites contain this value in a list. If that's the case, we generally only want the first item of the list.
    if "allrecipes" in str(parsed_url.netloc).lower():
        total_servings = re.sub('[^A-Za-z0-9]+', '', str(recipe_json[0]['recipeYield']))
    elif "thewoksoflife" in str(parsed_url.netloc).lower():
        total_servings = str(recipe_json['@graph'][7]['recipeYield'][0])
    elif type(recipe_json[0]['recipeYield']) == list:
        total_servings = recipe_json[0]['recipeYield'][0]
    else:
        total_servings = str(recipe_json[0]['recipeYield'])

    # Get the URL for the recipe image, create the image filename, and download the image:
    if "thewoksoflife" in str(parsed_url.netloc).lower():
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
