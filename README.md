# Chef GPT
---
> A chatbot that can understand user preferences for food recipes and provide suggestions from a pre-existing dataset.
---

## Table of Contents
* [In Action](#in-action)
* [Steps to Run the Project](#steps-to-run-the-project)
* [Dataset](#dataset)
* [System Design](#system-design)
* [Flow Chart](#flow-chart)
* [Conclusion](#conclusion)

## In Action

https://github.com/shruthipv96/ChefGPT/assets/32814013/296ac183-123f-43c9-a77a-068fc3d645ce

Detailed report of the project is available at [here](https://github.com/shruthipv96/ChefGPT/blob/main/ChefGPT.pdf).

## Steps to Run the Project 
### 1. Ensure OpenAI Account and API Keys: 
* Create an account on OpenAI if you don't have one. 
* Make sure you have enough credits to use the 'gpt-4o' model. 
* Obtain your API keys and save them in a file named Open_AI_Key.txt. 
### 2. Open the Project in Visual Studio Code: 
* Launch Microsoft Visual Studio Code on your computer. 
* Open the project folder in Visual Studio Code. 
### 3. Run the Main Application File: 
* Locate the app.py file in the project directory. 
* Execute the app.py file to start the chatbot. This file contains the initial flow of the code and will set everything in motion. 
### 4. You can open the webpage at http://127.0.0.1:5000/ to converse with the ChefGPT.

#### Note: 
* **Installation:** Run `pip install -r requirements.txt` to install all the dependencies.
* Since we are using online LLM models, sometimes response might be not as expected, so try again by clicking on ‘End Conversation’ button or restarting the application.

## Dataset
* The dataset used in this project is a refined version of the [6000+ Indian Food Recipes Dataset (kaggle.com)](https://www.kaggle.com/datasets/kanishk307/6000-indian-food-recipes-dataset) available on Kaggle.  
#### Modifications made to the original dataset:
1. Filtered for English Content 
2. The dataset was streamlined to include only the following relevant columns ('Srno', 'Recipe Name', 'Ingredients', 'PrepTimeInMins', 'CookTimeInMins', 'TotalTimeInMins', 'Servings', 'Cuisine', 'Course', 'Diet', 'Instructions', 'URL')

## System Design

![SystemDiagram](https://github.com/shruthipv96/ChefGPT/assets/32814013/1a937beb-d92b-4379-a702-6d4e3f027ea2)

## Flow Chart

![FlowChart](https://github.com/shruthipv96/ChefGPT/assets/32814013/8e0a0b51-20f8-4932-8e69-363f24778e93)


## Conclusion
With the ChefGPT developed, the user can interact with the bot to get a recipe of interest. 

### Key points
* Developed an end-to-end system starting from data source till recipe suggestion.
* Developed a feedback system to understand if the user is satisfied with the suggestion or else keep suggesting till we have enough data. 
* Implemented Function Calling API and biggest advantage is that it takes care of filling all the required data. 
* Experimented with different prompts to improvise the LLM model’s response. 
* Implemented this whole chatbot on a web interface. 

### Areas of Improvement
* Currently the knowledge of the chatbot is with respect to the food_recipe.xlsx file. We can expand that to fetch details from online sources. 
* Understanding the user requirements can be improved to fetch more details, like specific ingredients of choice or specific recipe names. 
* Feedback assistant could be improved to better understand the user satisfaction.

## Contact
Created by [Shruthip Venkatesh](https://github.com/shruthipv96) - feel free to contact me!
