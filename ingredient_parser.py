import spacy

produce = ['tarragon', 'parsley', 'garlic', 'apples', 'apple', 'onion', 'onions', 'herb', 'herbs',
           'banana', 'bananas', 'strawberry', 'strawberries', 'lemon', 'lemons', 'ginger', 'radish', 'radishes',
           'spinach', 'lettuce', 'cabbage', 'pepper', 'peppers', 'artichoke', 'artichokes', 'arugula', 'asparagus',
           'avocado', 'bamboo', 'sprout', 'sprouts', 'beans', 'beet', 'beets', 'endive', 'melon', 'melons', 'gourd',
           'gourds', 'bok choy', 'choi', 'pak choy', 'broccoli', 'brussels', 'calabash', 'carrot', 'carrots', 'yuca',
           'yucca', 'celery', 'chayote', 'corn', 'cucumber', 'daikon', 'edamame', 'eggplant', 'fennel', 'ginger',
           'grape', 'grapes', 'green bean', 'green beans', 'collards', 'collard greens', 'kale', 'kohlrabi', 'rapini',
           'swiss chard', 'spinach', 'turnip', 'turnips', 'artichoke', 'leek', 'leeks', 'lemongrass', 'mushroom',
           'mushrooms', 'okra', 'parsley', 'parsnip', 'pea', 'peas', 'plantain', 'potato', 'potatoes', 'pumpkin',
           'radicchio', 'rutabaga', 'shallots', 'squash', 'tomatillo', 'tomato', 'watercress', 'winter melon', 'yams',
           'zucchini']

meat = ['veal', 'pork', 'chicken', 'turkey', 'hot dog', 'salami', 'sausage', 'beef', 'venison']

dairy = ['cheese', 'egg', 'eggs', 'cream', 'yogurt', 'yoghurt', 'milk']

pasta_etc = ['pasta', 'spaghetti', 'noodles', 'rice']

cans_spices = ['canned', 'black pepper', 'salt', 'cumin']

test_list = ['1 pound uncooked spaghetti', '½ cup olive oil', '6 cloves garlic, thinly sliced',
             '¼ teaspoon red pepper flakes, or to taste', 'salt and freshly ground black pepper to taste',
             '¼ cup chopped fresh Italian parsley', '1 cup finely grated Parmigiano-Reggiano cheese']

test_list2 = ['4 dried guajillo chiles, stemmed and seeded', '2 tablespoons achiote paste',
             '6 large cloves garlic, peeled', '1 (7 ounce) can chipotle peppers in adobo sauce, drained',
             '1 ⅓ cups finely chopped onion, divided', '⅔ cup orange juice', '3 tablespoons apple cider vinegar',
             '3 tablespoons olive oil', '1 tablespoon ground cumin', '1 tablespoon light brown sugar',
             '1 teaspoon kosher salt', '3 pounds skinless, boneless chicken thighs, cut in half',
             '8 (12-inch) jumbo wooden skewers', '1 large fresh pineapple - peeled, cored, and sliced',
             '20 (6 inch) corn tortillas', '¼ cup roughly chopped fresh cilantro']

grammar = "NP: {<DT>?<JJ>*<NN>}"

test1 = '1 pound uncooked spaghetti'
test2 = '6 cloves garlic, thinly sliced'
test3 = '¼ cup chopped fresh Italian parsley'
test4 = '20 6 inch corn tortillas'

nlp = spacy.load("en_core_web_sm")

for ingredient in test_list2:
    doc = nlp(ingredient)
    for chunk in doc.noun_chunks:
        print(chunk.text)
