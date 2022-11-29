from bs4 import BeautifulSoup
import requests

# Recipe class that will be returned, which will contain all the necessary information for each recipe parses from
# the URL:


class Recipe:
    def __init__(self, title, prep, cook, rest, total, servings, ingredients, instructions):
        self.title = title
        self.prep = prep
        self.cook = cook
        self.rest = rest
        self.total = total
        self.servings = servings
        self.ingredients = ingredients
        self.instructions = instructions


def allrecipes_parse(url):
    result = requests.get(url)
    doc = BeautifulSoup(result.text, features="html.parser")

    recipe_details = doc.find(id="recipe-details_1-0")

    # The following if statements check to make sure the data we're looking for actually exists. If it does not,
    # it will assign the variable in question to "None indicated," to let the user know the recipe site did not provide
    # a value.

    if doc.find(id="article-heading_2-0") is not None:
        recipe_title = doc.find(id="article-heading_2-0")
        recipe_title = recipe_title.string
    else:
        recipe_title = "None indicated."

    if doc.find(text="Prep Time:").find_next("div") is not None:
        prep_time = doc.find(text="Prep Time:").find_next("div")
        prep_time = prep_time.string
    else:
        prep_time = "None indicated."

    if doc.find(text="Cook Time:").find_next("div") is not None:
        cook_time = doc.find(text="Cook Time:").find_next("div")
        cook_time = cook_time.string
    else:
        cook_time = "None indicated."

    if doc.find(text="Stand Time:") is not None:
        stand_time = doc.find(text="Stand Time:").find_next("div")
        stand_time = stand_time.string
    else:
        stand_time = "None indicated."

    if doc.find(text="Total Time:").find_next("div") is not None:
        total_time = doc.find(text="Total Time:").find_next("div")
        total_time = total_time.string
    else:
        total_time = "None indicated."

    if doc.find(text="Servings:").find_next("div") is not None:
        total_servings = doc.find(text="Servings:").find_next("div")
        total_servings = total_servings.string
    else:
        total_servings = "None indicated."

    # recipe_ingredients is a variable that will contain the raw HTML/CSS pertaining to the recipes. This raw data is
    # structured as an unordered list, and each list entry has a <p> tag surrounding it. The following line parses out
    # all the <p> tags within the list, and adds them to a Python list (BS does this automatically):

    recipe_ingredients = doc.find(class_="mntl-structured-ingredients__list").find_all("p")

    # This simple loop just goes through the above-generated list and further breaks it down by each <span> tag that
    # contains the data we're looking for. Allrecipes.com has three <span> tags for every ingredient, one containing
    # quantity, one containing unit of measurement, and one for type of ingredient. Each of these (quantity, unit of
    # measurement, etc) is added to its own list. The if statements check to make sure the value actually exists before
    # appending to the list:

    complete_ingredients = []

    for row in recipe_ingredients:
        if row.find_all("span")[0].string is None:
            quantity = ""
        else:
            quantity = row.find_all("span")[0].string + " "

        if row.find_all("span")[1].string is None:
            measurement = ""
        else:
            measurement = row.find_all("span")[1].string + " "

        if row.find_all("span")[2].string is None:
            ingredient = ""
        else:
            ingredient = row.find_all("span")[2].string

        concatenated_ingredients = quantity + measurement + ingredient
        complete_ingredients.append(concatenated_ingredients)

    recipe_instructions = doc.find(id="mntl-sc-block_2-0").find_all("li")
    parsed_instructions = []
    stripped_instructions = []

    # The following (clunky) code gets the raw HTML/CSS section for the recipe instructions, creates a list with
    # cleaned up instructions, and finally strips newlines out of the list. This leaves stripped_instructions
    # as the list containing all of the instructions for the recipe:

    for row in recipe_instructions:
        parsed_instructions.append(row.find_all("p")[0].string)

    for i in parsed_instructions:
        stripped_instructions.append(i.strip())

    recipe_data = Recipe(recipe_title.string, prep_time.string, cook_time.string, stand_time,
                         total_time.string, total_servings.string, complete_ingredients, stripped_instructions)

    return recipe_data
