# ----------------------------------------------------------------------
# Import Libraries
# ----------------------------------------------------------------------
import pandas as pd
import random

# ----------------------------------------------------------------------
# Load the pre-existing recipe database
# ----------------------------------------------------------------------
recipe_db = pd.read_excel('food_recipe.xlsx')

# ----------------------------------------------------------------------
# Below here are the recipe extraction functions
# ----------------------------------------------------------------------
def filterBasedOnPrepAndCookTime(userPrepTime, userCookTime, recipePrepTime, recipeCookTime, recipeTotalTime):
    '''
    Function to filter the recipe based on user provided prep and cook time
    '''
    # Calculate the ratio of preparation and cooking time from total recipe time
    prepRatio = recipePrepTime / recipeTotalTime
    cookRatio = recipeCookTime / recipeTotalTime
    
    # Based on user inputs, cross check with the ratio and return accordingly
    if (userPrepTime == 'less' and userCookTime == 'more'):
        if(prepRatio < cookRatio):
            return True
    if (userPrepTime == 'more' and userCookTime == 'less'):
        if(cookRatio < prepRatio):
            return True
    if (userPrepTime == 'more' and userCookTime == 'more'):
        # Since user has lot of time, any recipe should be fine
        return True
    if (userPrepTime == 'less' and userCookTime == 'less'):
        if(recipeTotalTime <= 30):
            return True
    return False

def get_food_recipes(recipe_requirement):
    '''
    Filter the recipes based on the user requirements for the requirement
    Provide a list of such valid recipes as output
    '''
    # Filter the recipe based on user interest of cuisine, diet and course
    filtered_recipes = recipe_db.loc[ recipe_db['Cuisine'] == recipe_requirement['Cuisine']]
    filtered_recipes = filtered_recipes.loc[filtered_recipes['Diet'] == recipe_requirement['Diet']]
    filtered_recipes = filtered_recipes.loc[filtered_recipes['Course'] == recipe_requirement['Course']]
    recipes = []
    for _, recipe in filtered_recipes.iterrows():
        # Filter the recipe based on preparation and cooking time
        isValid = filterBasedOnPrepAndCookTime(userPrepTime = recipe_requirement['PreparationTime'], userCookTime = recipe_requirement['CookingTime'],
                                          recipePrepTime = recipe['PrepTimeInMins'], recipeCookTime = recipe['CookTimeInMins'],
                                          recipeTotalTime = recipe['TotalTimeInMins'])
        if (isValid == True):
            # Generate the output dictionary
            validRecipe = {}
            validRecipe['Recipe Name'] = recipe['Recipe Name'].replace(u'\\xa0', u'')
            validRecipe['Ingredients'] = recipe['Ingredients'].replace(u'\\xa0', u'')
            validRecipe['PrepTimeInMins'] = recipe['PrepTimeInMins']
            validRecipe['CookTimeInMins'] = recipe['CookTimeInMins']
            validRecipe['Instructions'] = recipe['Instructions'].replace(u'\\xa0', u'')
            validRecipe['URL'] = recipe['URL']
            validRecipe['RecipeServings'] = int(recipe['Servings'])
            validRecipe['UserServings'] = int(recipe_requirement['Servings'])
            recipes.append(validRecipe)
    return recipes

def generate_recipe_report(recipe):
    '''
    Function which generates a report in HTML format from a dictionary
    '''
    if recipe == '':
        return ''
    
    report = "<ul>"
    report = f"<strong>Recipe Name:</strong> {recipe['Recipe Name']} <br><br>"
    report+= f"<strong>Preparation Time:</strong> {recipe['PrepTimeInMins']} <br><br>"
    report+= f"<strong>Cooking Time:</strong>  {recipe['CookTimeInMins']} <br><br>"
    report+= f"<strong>Ingredients:</strong> <br>"
    ingredients = recipe['Ingredients'].split(',')
    for step in ingredients:
        if step.strip() == '':
            continue
        report+= f"<li>{step+'.'}</li>"
    report+= '<br>'
    report+= f"<strong>Instructions:</strong> <br>"
    instructions = recipe['Instructions'].split('.')
    for step in instructions:
        if step.strip() == '':
            continue
        report+= f"<li>{step.strip()+'.'}</li>"
    report+= '<br>'
    if recipe['RecipeServings'] > recipe['UserServings']:
        report += f"<strong>Servings:</strong> <br> Instructions are for {recipe['RecipeServings']} people. \
            Remember to scale down ingredients accordingly for {recipe['UserServings']} people."
    elif recipe['RecipeServings'] < recipe['UserServings']:
        report += f"<strong>Servings:</strong> <br> Instructions are for {recipe['RecipeServings']} people. \
            Remember to scale up ingredients accordingly for {recipe['UserServings']} people."
    else:
        report += f"<strong>Servings:</strong> <br> Servings will be for {recipe['UserServings']} "
    report += f'<br><br>For more details, you can refer at <a href="{recipe['URL']}" target="_blank">{recipe['URL'] }</a>'
    report += "</ul>"

    return report

def get_random_recipe(recipes, explained_recipes):
    '''
    Selects a random recipe from the list of valid recipes that hasn't been 
    explained yet and generates its HTML report. 
    '''
    n_recipes = len(recipes)-1
    for _ in range(n_recipes) :
        # Pick a random index for list
        index = random.randint(0,n_recipes)

        # Check if the recipe is not suggested already
        if index not in explained_recipes:
            # Fetch the recipe dictionary and convert it into HTML report
            recipe = recipes[index]
            explained_recipes.append(index)
            recipe_report = generate_recipe_report(recipe=recipe)
            return recipe_report, explained_recipes
    return None, []
    
    

