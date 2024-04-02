# RecipeDB

Welcome to the GitHub repository of INC0GN1T0, an advanced web application designed to manage a wide range of recipes and ingredients. Our team has been working tirelessly to bring this project to life, integrating an API for recipe retrieval and implementing databases for efficient management. A user can log in and look up many different recipes, that come either from an API specialized in meals or that other users made and added to the database. The user can also add recipes from the API, or add their custom ones. There are other advanced features such as managing the ingredients they own, the ones they are allergic to; and organizing recipes into menus.

The application is live and can be accessed at https://recipes.coolidges.ca/.

## Local Setup

To run the project locally, you need to create a Python virtual environment and install the required packages.

### Install Required Packages
```
pip3 install -r requirements.txt
```
### Start the app
```
python 3 main.py
```
The console messages will show the local port the application is running on, and it will log the application's progress.



# Key Features
#### Login system: Users can create an account with a profile picture and the user info is saved securely in the database.
#### Recipes: Random selection of recipes displayed on the home-page.
#### My recipes: Displays recipes added from the API by you or created by you.
#### Browse recipes: With a keyword, look for recipes in our database. Keep the input field blank to browse the entire database.
#### Saved recipes: Search all the recipes you saved. Think of this as your “bookmarked” recipes.
#### Add recipes:
   - Manually: fill out a form and add a recipe to the database
   - Lookup: get a selection of recipes by searching the API with a prompt, and select one to add it to the database.
#### Menus:
   - Display: your saved menus.
   - Add to menu: add recipes to your menus, and organize them however you want.
#### Profile (click the “Let’s get cooking! <username> to access it):
  - Manage ingredients (for both ingredients one is allergic to and ingredients one owns, the functionalities are the same in this menu)
     - View ingredients (owned/allergic).
     - Add/Remove an ingredient from the respective list.



# User Manual
For a step by step instructions on how to use the app and its features, please visit:
https://docs.google.com/document/d/15d_t0Oh07p6Pd5dMLicyGzQi9gifZmzqfgRCh0Vgp6g/edit?usp=sharing
