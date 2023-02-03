from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import shutil
import json
import isodate
import re
from datetime import date


# Recipe class that will be returned, which will contain all the necessary information for each recipe parsed from
# the URL:
class Recipe:
    """This class stores the parsed recipe, and is returned by the parser.
    """
    def __init__(self, title, prep, cook, rest, total, servings, ingredients, instructions, image, ingredient_list,
                 original_url, date_parsed, instructions_json):
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
        self.original_url = original_url
        self.date_parsed = date_parsed
        self.instructions_json = instructions_json


def download_image(url, file_name):
    """Function to download and store recipe images. Essentially copy/pasted from
    https://www.scrapingbee.com/blog/download-image-python/

    :param url: source URL for the image to be downloaded
    :param file_name: file name under which to save the downloaded image
    :return: does not return a value, simply saves the image to disk
    """
    res = requests.get(url, stream=True)
    file_name = "./website/static/" + file_name

    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
    else:
        print('Image Couldn\'t be retrieved')


def get_time(iso_time):
    """Converts the ISO8601 time from the recipe schema into human readable time. Big thanks to
    StackOverflow for providing the isodate solution.

    :param iso_time: time in the ISO8601 format such as "PT10M"
    :return parsed_time: should be a human readable string such as "1 hour and 10 minutes":
    """
    parsed_time = isodate.parse_duration(iso_time)
    parsed_time_list = str(parsed_time).split(":")

    if parsed_time_list[0] == "1" and parsed_time_list[1] != "00":
        parsed_time = parsed_time_list[0] + " hour and " + parsed_time_list[1] + " minutes"
        return str(parsed_time)
    elif parsed_time_list[0] != "0" and parsed_time_list[1] == "00":
        if parsed_time_list[0] == "1":
            parsed_time = parsed_time_list[0] + " hour"
            return str(parsed_time)
        else:
            parsed_time = parsed_time_list[0] + " hours"
            return str(parsed_time)
    else:
        parsed_time = parsed_time_list[1] + " minutes"
        return str(parsed_time)


def recipe_parser(url):
    """Main recipe parser. Takes a recipe URl and returns a parsed recipe ready to be stored in the database.

    :param url: URL of website to be parsed

    :return recipe_data: Recipe class object containing the title, prep time, cook time, rest time (if any), total
    time to make recipe, amount of servings, ingredients, recipe instructions, recipe image, and a Python list of
    all ingredients.
    """

    # User-Agent header information in case the target website blocks scrapers:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/74.0.3729.169 Safari/537.36"
    }

    # Parse URL into components for later checking of which website the recipe is from:
    parsed_url = urlparse(url)

    # Get current date so we know when the recipe was originally parsed:
    current_date = date.today()
    current_date = current_date.strftime("%B %d, %Y")

    result = requests.get(url, headers=headers)
    doc = BeautifulSoup(result.text, features="html.parser")

    try:
        recipe_details = doc.find(type="application/ld+json")
        recipe_json = json.loads(recipe_details.text)
    except:
        print("Failed to retrieve LD+JSON data from " + url)
        return 1

    # Store all ingredients with HTML formatting in a single variable. Used for recipe preview before it is
    # saved to the database.
    joined_ingredients = ""

    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "recipeIngredient" in json_key.keys():
                        for ingredient in json_key.get('recipeIngredient'):
                            joined_ingredients += "<li>" + ingredient + "</li><br>"
            elif "recipeIngredient" in recipe_json.keys():
                for ingredient in recipe_json.get('recipeIngredient'):
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
    except:
        print("Failed to parse ingredients from " + url)

    # Store all instructions with HTML formatting in a single variable. Used for recipe preview before it is
    # saved to the database.
    joined_instructions = ""

    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "recipeInstructions" in json_key.keys():
                        for instruction in json_key.get('recipeInstructions'):
                            joined_instructions += "<li>" + instruction['text'] + "</li><br>"
            elif "recipeInstructions" in recipe_json.keys() and isinstance(recipe_json.get('recipeInstructions'), list):
                for instruction in recipe_json.get('recipeInstructions'):
                    joined_instructions += "<li>" + instruction.get('text') + "</li><br>"
        elif isinstance(recipe_json, list):
            for item in recipe_json:
                if isinstance(item, dict) and "recipeInstructions" in item.keys():
                    if isinstance(item.get('recipeInstructions'), list):
                        for instruction in item.get('recipeInstructions'):
                            joined_instructions += "<li>" + instruction.get('text') + "</li><br>"
        elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
            for instruction in recipe_json['@graph'][7].get('recipeInstructions'):
                joined_instructions += "<li>" + instruction['text'] + "</li><br>"
        else:
            for instruction in recipe_json[0].get('recipeInstructions'):
                joined_instructions += "<li>" + instruction['text'] + "</li><br>"
    except:
        print("Failed to get recipe instructions from " + url)

    # Store a Python list of instructions and ingredients. Ingredient list is used to iterate over and generate
    # shopping list.
    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "recipeInstructions" in json_key.keys():
                        ingredient_list = json_key.get('recipeIngredient')
                        instruction_list = json_key.get('recipeInstructions')
            elif "recipeInstructions" in recipe_json.keys():
                ingredient_list = recipe_json.get('recipeIngredient')
                instruction_list = recipe_json.get('recipeInstructions')
        elif isinstance(recipe_json, list):
            for item in recipe_json:
                if isinstance(item, dict) and "recipeInstructions" in item.keys():
                    if isinstance(item.get('recipeInstructions'), list):
                        ingredient_list = item.get('recipeIngredient')
                        instruction_list = item.get('recipeInstructions')
        elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
            ingredient_list = recipe_json['@graph'][7].get('recipeIngredient')
            instruction_list = recipe_json['@graph'][7].get('recipeInstructions')
        else:
            ingredient_list = recipe_json[0].get('recipeIngredient')
            instruction_list = recipe_json[0].get('recipeInstructions')
    except:
        print("Failed to generate recipe ingredient and instruction lists from " + url)

    instructions_dict = {}

    for i, instruction in zip(range(len(instruction_list)), instruction_list):
        instructions_dict[i] = instruction.get('text')

    instructions_dict = json.dumps(instructions_dict)

    # Parse the ISO8601 time into human readable time:
    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "cookTime" in json_key.keys():
                        cook_time = get_time(json_key.get('cookTime'))
                    if "prepTime" in json_key.keys():
                        prep_time = get_time(json_key.get('prepTime'))
            elif "cookTime" in recipe_json.keys() and "prepTime" in recipe_json.keys():
                cook_time = get_time(recipe_json.get('cookTime'))
                prep_time = get_time(recipe_json.get('prepTime'))
            else:
                cook_time = get_time(recipe_json.get('cookTime'))
                prep_time = "Not specified."
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
    except:
        cook_time = "Not specified"
        prep_time = "Not specified"
        print("Failed to parse prep and cook time from " + url)

    # Check to see if recipe has a rest time. If not, set rest time to 0 minutes:
    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "restTime" in json_key.keys():
                        rest_time = get_time(json_key.get('restTime', "PT0M"))
                    else:
                        rest_time = get_time("PT0M")
            elif "restTime" in recipe_json.keys():
                rest_time = get_time(recipe_json.get('restTime'))
            else:
                rest_time = "PT0M"
        elif isinstance(recipe_json, list):
            for item in recipe_json:
                if isinstance(item, dict) and "restTime" in item.keys():
                    rest_time = get_time(item.get('restTime'))
                else:
                    rest_time = get_time("PT0M")
        elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
            rest_time = get_time(recipe_json['@graph'][7].get('restTime', 'PT0M'))
        else:
            rest_time = get_time(recipe_json[0].get('restTime', 'PT0M'))
    except:
        print("Failed to parse rest time from " + url)

    # Get total time for recipe:
    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "totalTime" in json_key.keys():
                        total_time = get_time(json_key.get('totalTime'))
                        break
            elif "totalTime" in recipe_json.keys():
                total_time = get_time(recipe_json.get('totalTime'))
            else:
                total_time = "Not specified."
        elif isinstance(recipe_json, list):
            for item in recipe_json:
                if isinstance(item, dict) and "totalTime" in item.keys():
                    total_time = get_time(item.get('totalTime'))
                    break
        elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
            total_time = get_time(recipe_json['@graph'][7]['totalTime'])
        else:
            total_time = get_time(recipe_json[0]['totalTime'])
    except:
        total_time = "Not specified"
        print("Failed to get total time from " + url)

    # Get the recipe title:
    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "name" in json_key.keys():
                        recipe_title = json_key.get('name')
                        break
            elif "name" in recipe_json.keys():
                recipe_title = recipe_json.get("name")
        elif isinstance(recipe_json, list):
            for item in recipe_json:
                if isinstance(item, dict) and "name" in item.keys():
                    recipe_title = item.get('name')
                    break
        elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
            recipe_title = recipe_json['@graph'][7]['name']
        else:
            recipe_title = recipe_json[0]['headline']
    except:
        print("Failed to get recipe title from " + url)

    # Get the amount of servings. Allrecipes returns a weird value, so it has to be cleaned up. Also
    # some websites contain this value in a list. If that's the case, we generally only want the first item of the list.
    try:
        if "allrecipes" in str(parsed_url.netloc).lower():
            total_servings = re.sub('[^A-Za-z0-9]+', '', str(recipe_json[0]['recipeYield']))
        elif isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "recipeYield" in json_key.keys():
                        total_servings = str(json_key.get('recipeYield')[0])
                    else:
                        total_servings = "Not specified"
            elif "recipeYield" in recipe_json.keys() and recipe_json.get('recipeYield') is not None:
                if isinstance(recipe_json.get('recipeYield'), list):
                    total_servings = str(recipe_json.get('recipeYield')[0])
                else:
                    total_servings = str(recipe_json.get('recipeYield'))
            else:
                total_servings = "Not specified"
        elif isinstance(recipe_json, list):
            for item in recipe_json:
                if isinstance(item, dict) and "recipeYield" in item.keys() and isinstance(item.get('recipeYield'), list):
                    total_servings = str(item.get('recipeYield')[0])
                else:
                    total_servings = str(item.get('recipeYield'))
        elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
            total_servings = str(recipe_json['@graph'][7]['recipeYield'][0])
        elif type(recipe_json[0]['recipeYield']) == list:
            total_servings = str(recipe_json[0]['recipeYield'][0])
        else:
            total_servings = str(recipe_json[0]['recipeYield'])
    except:
        print("Failed to get serving amount from " + url)

    # Get the URL for the recipe image, create the image filename, and download the image:
    try:
        if isinstance(recipe_json, dict):
            if "@graph" in recipe_json.keys():
                for json_key in recipe_json.get('@graph'):
                    if "@type" in json_key.keys():
                        if json_key.get('@type') == "ImageObject":
                            image_url = json_key.get('url')
            elif "@graph" in recipe_json.keys():
                for json_key in recipe_json['@graph']:
                    if "image" in json_key.keys():
                        image_url = json_key.get('image')
                        if isinstance(image_url, dict):
                            image_url = list(image_url.values())[0]
                            break
            elif "image" in recipe_json.keys() and isinstance(recipe_json.get("image"), list):
                if "url" in recipe_json.get("image")[0]:
                    image_url = recipe_json.get("image")[0].get("url")
                else:
                    image_url = recipe_json.get("image")[0]
            else:
                image_url = recipe_json.get("image")
        elif isinstance(recipe_json, list):
            for item in recipe_json:
                if isinstance(item, dict) and "image" in item.keys():
                    if isinstance(item.get('image'), dict):
                        image_url = item.get('image').get('url')
                    else:
                        image_url = item.get('image')
                        print(image_url)
        elif recipe_json['@graph'][7].get('@context') == "https://schema.org/":
            image_url = recipe_json['@graph'][7]['image'][0]
        else:
            image_url = recipe_json[0]['image']['url']

        image_title = recipe_title.strip()
        image_title = re.sub('[^A-Za-z0-9]+', '', image_title) + ".jpg"
        download_image(image_url, image_title)
    except:
        print("Failed to parse image url from " + url)

    recipe_data = Recipe(recipe_title, prep_time, cook_time, rest_time,
                         total_time, total_servings, joined_ingredients, joined_instructions, image_title,
                         ingredient_list, url, current_date, instructions_dict)

    return recipe_data
