from bs4 import BeautifulSoup
import requests

url = "https://www.allrecipes.com/recipe/8510539/baked-turkey-riggies/"
result = requests.get(url)

doc = BeautifulSoup(result.text, features="html.parser")
recipe_title = doc.find(id="article-heading_2-0")

recipe_details = doc.find(id="recipe-details_1-0")

prep_time = doc.find(text="Prep Time:").find_next("div")
# print("Prep Time: ", prep_time.string)

cook_time = doc.find(text="Cook Time:").find_next("div")
# print("Cook Time: ", cook_time.string)

stand_time = doc.find(text="Stand Time:").find_next("div")
# print("Stand Time: ", stand_time.string)

total_time = doc.find(text="Total Time:").find_next("div")
# print("Total Time: ", total_time.string)

total_servings = doc.find(text="Servings:").find_next("div")
# print("Total Servings: ", total_servings.string)

# recipe_ingredients is a variable that will contain the raw HTML/CSS pertaining to the recipes. This raw data is
# structured as an unordered list, and each list entry has a <p> tag surrounding it. The following line parses out
# all the <p> tags within the list, and adds them to a Python list (BS does this automatically):

recipe_ingredients = doc.find(class_="mntl-structured-ingredients__list").find_all("p")

# This simple loop just goes through the above-generated list and further breaks it down by each <span> tag that
# contains the data we're looking for. Allrecipes.com has three <span> tags for every ingredient, one containing
# quantity, one containing unit of measurement, and one for type of ingredient:

# for row in recipe_ingredients:
#    print(row.find_all("span")[0].string, row.find_all("span")[1].string, row.find_all("span")[2].string)

recipe_instructions = doc.find(id="mntl-sc-block_2-0").find_all("li")
for row in recipe_instructions:
    print(row.find_all("p")[0].string)
