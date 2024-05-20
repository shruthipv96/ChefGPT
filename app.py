# ----------------------------------------------------------------------
# Import Libraries
# ----------------------------------------------------------------------
from flask import Flask, redirect, url_for, render_template, request
import openai
import json
from food_recipe import get_food_recipes, get_random_recipe
from functions import initialize_conversation, initialize_conv_reco, get_chat_model_completions, moderation_check
 
# ----------------------------------------------------------------------
# Setup Open AI Key and Flask server
# ----------------------------------------------------------------------
openai.api_key = open("Open_AI_Key.txt", "r").read().strip()

app = Flask(__name__)

# ----------------------------------------------------------------------
# Initialize global variables and generate a welcome note
# ----------------------------------------------------------------------
conversation_bot = []
conversation_reco = []
conversation = initialize_conversation()
introduction = get_chat_model_completions(conversation)
introduction = introduction.message["content"]
conversation_bot.append({'bot':introduction})
recipes = None
explained_recipes = []

# ----------------------------------------------------------------------
# Flask Route : Default path
# ----------------------------------------------------------------------
@app.route("/")
def default_func():
    global conversation_bot
    # Render the page
    return render_template("index_chat.html", content = conversation_bot)

# ----------------------------------------------------------------------
# Flask Route : End conversation resets the global variables
# ----------------------------------------------------------------------
@app.route("/end_conv", methods = ['POST','GET'])
def end_conv():
    global conversation_bot, conversation, recipes, explained_recipes, conversation_reco
    # Reset the global variables
    conversation_bot = []
    conversation_reco = []
    conversation = initialize_conversation()
    introduction = get_chat_model_completions(conversation)
    introduction = introduction.message["content"]
    conversation_bot.append({'bot':introduction})
    recipes = None
    explained_recipes = []
    return redirect(url_for('default_func'))

# ----------------------------------------------------------------------
# Flask Route : Chat method implementing dialogue management system
# ----------------------------------------------------------------------
@app.route("/chat", methods = ['POST'])
def chat():
    global conversation_bot, conversation, recipes, explained_recipes, conversation_reco

    # Fetch and check the user input moderation
    user_input = request.form["user_input_message"]
    prompt = '\nRemember your system message and that you are an intelligent chef. So, you only help with questions around food and its recipes.'
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('end_conv'))

    # If the recipe list is not available
    if recipes is None:
        print('---- Understanding the user requirement ----')

        # Append the user input to appropriate global variables
        conversation.append({"role": "user", "content": user_input + prompt})
        conversation_bot.append({'user':user_input})

        # Converse with the chat api
        reply = get_chat_model_completions(conversation)

        # Fetch and check the assistant response moderation
        response_assistant = reply.message["content"]
        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))
        conversation.append({"role": "assistant", "content": response_assistant})
        print('Response from API:\n', reply)

        # Check for function call trigger to fetch food recipes
        if 'tool_calls' in reply.message.keys():
            tool_call = reply.message['tool_calls'][0]
            if tool_call and tool_call.function.name == "get_food_recipe":
                print('Making a function call to fetch the recipes')

                # Extract the arguments for the function call
                function_args = json.loads(tool_call.function.arguments)
                recipe = {
                    'Cuisine' : function_args.get("Cuisine"),
                    'Course'  : function_args.get("Course"),
                    'Diet'    : function_args.get("Diet"),
                    'PreparationTime' : function_args.get("PreparationTime"),
                    'CookingTime' : function_args.get("CookingTime"),
                    'Servings': function_args.get("Servings")
                }

                # Append the bot response to appropriate global variables
                conversation_bot.append({'bot':"Thank you for providing all the information. Kindly wait, while I fetch the recipes... \n"})

                # Fetch the food recipe
                recipes = get_food_recipes(recipe_requirement=recipe)

                # Check if there is a valid list of recipes matching user requirement
                if len(recipes) == 0:
                    conversation_bot.append({'bot':"Sorry, I do not have recipes that match your requirements. Please end this conversation."})
                else:
                    # Provide a random food recipe suggestion
                    suggestedRecipe, explained_recipes = get_random_recipe(recipes=recipes, explained_recipes=[])
                    conversation_bot.append({'bot':suggestedRecipe})

                    # Initialize a feedback assistant
                    conversation_reco = initialize_conv_reco()
                    satisfied = get_chat_model_completions(conversation_reco, needTools=False)
                    print('Response from Feedback call:\n', satisfied)
                    satisfied = satisfied.message["content"]
                    moderation = moderation_check(satisfied)
                    if moderation == 'Flagged':
                        return redirect(url_for('end_conv'))
                    # Append the bot response to appropriate global variables
                    conversation_reco.append({"role": "assistant", "content": satisfied})
                    conversation_bot.append({'bot':satisfied})

        # There is no function call, just add the assistant respose to appropriate global variable
        else:
            conversation_bot.append({'bot':response_assistant})

    # There is a known list of valid recipes
    else:
        print('---- Conversing with known list of recipes ----')

        # Append the user input to appropriate global variables
        conversation_reco.append({"role": "user", "content": user_input})
        conversation_bot.append({'user':user_input})

        # Converse with the chat api
        response_asst_reco = get_chat_model_completions(conversation_reco, needTools=False)

        # Fetch and check the assistant response moderation
        print('Response from API:\n ', response_asst_reco)
        feedback= response_asst_reco.message["content"]
        moderation = moderation_check(feedback)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))
        conversation_reco.append({"role": "assistant", "content": feedback})

        # Check for user satisfaction
        if (feedback == "No"):
            # If not satisfied, then provide random food recipe suggestion
            suggestedRecipe, explained_recipes = get_random_recipe(recipes=recipes, explained_recipes=explained_recipes)
            if suggestedRecipe is None:
                # If there is no recipe available, update the user with an apology note.
                conversation_bot.append({'bot':"Sorry, I do not have recipes that match your requirements. Please end this conversation."})
            else:
                # If there is recipe available, append the bot response to appropriate global variables
                conversation_bot.append({'bot':suggestedRecipe})
                conversation_bot.append({'bot':'How about this recipe?'})
        elif (feedback == "Yes"):
            # If satisfied, then update the user with a thanks note.
            conversation_bot.append({'bot': "Thank you for using the assistance ! Enjoy your food !"})
        elif (feedback == "Reset"):
            # If user wants to check with different requirements, reset the conversation.
            return redirect(url_for('end_conv'))
        else:
            # Append the bot response to appropriate global variables
            conversation_bot.append({'bot':feedback})

    return redirect(url_for('default_func'))

# ----------------------------------------------------------------------
# Main driver function
# ----------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host= "0.0.0.0")