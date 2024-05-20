# ----------------------------------------------------------------------
# Import Libraries
# ----------------------------------------------------------------------
import openai

# ----------------------------------------------------------------------
# Setup the values for cuisine, course and diet list supported by
# ChefGPT. These values are extracted from the food_recipe.xlsx file
# ----------------------------------------------------------------------
cuisine_list = ('Indian', 'South Indian Recipes', 'Andhra', 'Udupi', 'Mexican', 'Fusion', 'Continental', 'Bengali Recipes', 'Punjabi', 'Chettinad', \
    'Tamil Nadu', 'Maharashtrian Recipes', 'North Indian Recipes', 'Italian Recipes', 'Sindhi', 'Thai', 'Chinese', 'Kerala Recipes', 'Gujarati Recipes', 'Coorg', 'Rajasthani', 'Asian', \
    'Middle Eastern', 'Coastal Karnataka', 'European', 'Kashmiri', 'Karnataka', 'Lucknowi', 'Hyderabadi', 'Side Dish', 'Goan Recipes', \
    'Arab', 'Assamese', 'Bihari', 'Malabar', 'Himachal', 'Awadhi', 'Cantonese', 'North East India Recipes', 'Sichuan', 'Mughlai', 'Japanese', 'Mangalorean', 'Vietnamese', 'British', \
    'North Karnataka', 'Parsi Recipes', 'Greek', 'Nepalese', 'Oriya Recipes', 'French', 'Indo Chinese', 'Konkan', \
    'Mediterranean', 'Sri Lankan', 'Haryana', 'Uttar Pradesh', 'Malvani', 'Indonesian', 'African', 'Shandong', 'Korean', \
    'American', 'Kongunadu', 'Pakistani', 'Caribbean','South Karnataka', 'Appetizer', 'Uttarakhand-North Kumaon', \
    'World Breakfast', 'Malaysian', 'Dessert', 'Hunan', 'Dinner','Snack', 'Jewish', 'Burmese', 'Afghan', 'Brunch', 'Jharkhand', \
    'Nagaland')

course_list = ('Side Dish', 'Main Course', 'South Indian Breakfast', 'Lunch','Snack', 'Dinner', 'Appetizer', 'Indian Breakfast', 'Dessert', \
              'North Indian Breakfast', 'One Pot Dish', 'World Breakfast', 'No Onion No Garlic (Sattvic)', 'Brunch', 'Vegan', 'Sugar Free Diet')

diet_list = ('Diabetic Friendly', 'Vegetarian', 'High Protein Vegetarian', 'Non Vegeterian', 'High Protein Non Vegetarian', 'Eggetarian', \
    'Vegan', 'No Onion No Garlic (Sattvic)', 'Gluten Free', 'Sugar Free Diet')

# ----------------------------------------------------------------------
# Setup variables to be used in OpenAPI calls
# ----------------------------------------------------------------------
delimiter = "####"
MODEL_NAME= "gpt-4o"

# ----------------------------------------------------------------------
# Setup function call JSON structure to be set which calling OpenAI API
# ----------------------------------------------------------------------
requirement_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_food_recipe",
            "description": "Get the recipe for the food requested by the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "Cuisine": {
                        "type": "string",
                        "description": "The cuisine of interest. Eg:- Indian, Mexican",
                        "enum": cuisine_list
                    },
                    "Course": {
                        "type": "string",
                        "description": "The course of interest. Eg:- Lunch, Snack, Side dish",
                        "enum": course_list
                    },
                    "Diet": {
                        "type": "string",
                        "description": "The diet of interest. Eg:- Vegetarian, Non Vegetarian, Eggetarian",
                        "enum": diet_list
                    },
                    "PreparationTime": {
                        "type": "string",
                        "description": "The time taken for preparation",
                        "enum": ["more", "less"]
                    },
                    "CookingTime": {
                        "type": "string",
                        "description": "The time taken for cooking",
                        "enum": ["more", "less"]
                    },
                    "Servings": {
                        "type": "integer",
                        "description": "The number of people who will be enjoying the meal. Eg:- 5, 10. It cannot be a float or an impossible number like more than 1000.",
                    }
                },
                "required": ["Cuisine", "Course", "Diet", "PreparationTime", "CookingTime", "Servings"],
            },
        },
    }
]

# ----------------------------------------------------------------------
# Below here are the Open API related functions
# ----------------------------------------------------------------------
def get_chat_model_completions(messages, needTools=True):
    '''
    - Interacts with OpenAI's GPT model to get responses based on the conversation 
      history (messages).
    - If needTools is True, the api call includes the defined requirement_tools to 
      suggest recipes and implement function calling. 
    '''
    if needTools:
        # Complete chat with function call setup
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5, # this is the degree of randomness of the model's output
            max_tokens = 300,
            tools = requirement_tools,
            tool_choice ='auto'
        )
    else:
         # Complete chat without function call setup
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5, # this is the degree of randomness of the model's output
            max_tokens = 300,
        )

    return response.choices[0] 

def moderation_check(user_input):
    '''
    - Checks the user input for any inappropriate content using OpenAI's moderation API. 
    - Returns "Flagged" if the content is inappropriate, otherwise returns "Not Flagged". 
    '''
    if user_input == None:
        return "Flagged"

    response = openai.Moderation.create(input=user_input)
    moderation_output = response["results"][0]
    if moderation_output["flagged"] == True:
        return "Flagged"
    else:
        return "Not Flagged"

def initialize_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''
    global cuisine_list, diet_list, course_list, delimiter

    example_user_req = {'Cuisine': 'Indian', \
                        'Course' : 'Dessert', \
                        'Diet' : 'Vegetarian', \
                        'PreparationTime': 'less', \
                        'CookingTime': 'more', \
                        'Servings': '5'}

    response_format =  {'Cuisine': '_', \
                        'Course' : '_', \
                        'Diet' : '_', \
                        'PreparationTime': '_', \
                        'CookingTime': '_', \
                        'Servings': '_'}

    system_message = f"""

    You are an intelligent chef with an IQ of 150 and provide food recipes and suggestions based on user request.
    You need to ask relevant questions and understand the user requirement by analysing the user's responses.
    Your final objective is to fill the values for the different keys ('Cuisine', 'Course', 'Diet', 'PreparationTime', 'CookingTime', 'Servings') in the python dictionary and be confident of the values.
    These key value pairs define the user's requirement.
    The final response should in the {response_format} format with JSON value filled in the issue key. The response must be in JSON format with no additional text else you will be heavily penalized.
    And make a function call when the above JSON is available, else you will be heavily penalized.
   
    {delimiter}Here are the instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - The value for 'Cuisine' key should be one among in this list {cuisine_list}.
    - The value for 'Course' key should be one among in this list {course_list}. Map the user response to one among from this list. Example, main can be mapped to 'Main Course'.
    - The value for 'Diet' key should be one among in this list {diet_list}. Map the user response to one among from this list. Example, egg-based can be mapped to 'Eggetarian'. veg can be mapped to 'Vegetarian'.
    - The value for 'PreparationTime' key should be either 'less' or 'more'.
    - The value for 'CookingTime' key should be either 'less' or 'more'.
    - The value for 'Servings' key should be a plausible integer value. It cannot be a float or an impossible number like more than 1000.
    If the user is not able to provide expected response, provide some randomly picked example valid response from the defined list.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    {delimiter} Thought 1: Ask a question to understand the user's profile and requirements. \n
    If their primary need for recipe is unclear. Ask another question to comprehend their needs.
    You are trying to fill the values of all the keys ('Cuisine', 'Course', 'Diet', 'PreparationTime', 'CookingTime', 'Servings') in the python dictionary by understanding the user requirements.
    Identify the keys for which you can fill the values confidently using the understanding. \n
    Remember the instructions around the values for the different keys. 
    Answer "Yes" or "No" to indicate if you understand the requirements and have updated the values for the relevant keys. \n
    If yes, proceed to the next step. Otherwise, rephrase the question to capture their profile. \n{delimiter}

    {delimiter}Thought 2: Now, you are trying to fill the values for the rest of the keys which you couldn't in the previous step. 
    Remember the instructions around the values for the different keys. Ask questions you might have for all the keys to strengthen your understanding of the user's profile.
    Answer "Yes" or "No" to indicate if you understood all the values for the keys and are confident about the same. 
    If yes, move to the next Thought. If no, ask question on the keys whose values you are unsure of. \n
    It is a good practice to ask question with a sound logic as opposed to directly citing the key you want to understand value for.{delimiter}

    {delimiter}Thought 3: Check if you have correctly updated the values for the different keys in the python dictionary. 
    If you are not confident about any of the values, ask clarifying questions. {delimiter}

    {delimiter}Thought 4: User input might contain values for multiple keys. Be intelligent enough to distinguish between each.
    An example user input might look like,
    Input : Indian veg side dish. This is mapped to {{'Cusisine' : 'Indian', 'Course' : 'Side Dish', 'Diet' : 'Vegetarian'}}
    {delimiter}

    {delimiter}Thought 5: Once the necessary data is obtained from the previous steps, make a function call.
    If you are not confindent about making the function call, ask questions to confirm if the user wants to make any more changes.
    {delimiter}

    Follow the above chain of thoughts and only output the final updated python dictionary in JSON format. \n

    {delimiter} Here is a sample conversation between the user and assistant:
    User: "Hi, I want a recipe for Indian cuisine."
    Assistant: "Great! Indian cuisine provides lot of varieties. Are you looking for a main course?"
    User: "I am looking for a dessert."
    Assistant: "There are lot of delicious desserts based on eggs.
    User: "No, I am looking for a vegetarian dessert."
    Assistant: "No worries. We do have a variety in that, do you have more or less time to cook?"
    User: "I have less time to prepare and more time to cook."
    Assistant:"Perfect! And how many people would be enjoying the meal?"
    User: "There will be around 5 people"
    Assistant: "{example_user_req}"
    {delimiter}
    The above sample conversation is for reference and post that there will be a function call. If the function call is not triggered, you will be heavily penalized.
    Try to be more creative with the responses and the vocabulary.
    Start with a short creative welcome message and encourage the user to share their requirements.
    Do not start with Assistant: "
    """

    conversation = [{"role": "system", "content": system_message}]
    return conversation

def initialize_conv_reco():
    '''
    Initializes a separate conversation context for understanding user satisfaction with the recipe suggestions. 
    '''

    system_message = f"""
    You are an intelligent person who can understand if the user is satisfied with his food recipe suggestion.
    You must provide the output as "Yes", "No" or "Reset", else you will be heavily penalized.
    {delimiter}
    - If the user is satisfied with the suggestion, output as  "Yes".
    - If the user is not satisfied with the suggestion, output as "No" and check if the user wants some other recipe with same preferences.
    - If the user wants to modify the preference, output as "Reset".
    {delimiter}

    Start with a short message to understand the user satisfaction. Do not start with Assistant:
    Be polite to understand the user satisfaction.
    """

    conversation = [{"role": "system", "content": system_message }]
    return conversation