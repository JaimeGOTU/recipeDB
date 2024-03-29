import requests
import json
import pymysql

class RecipeAPI:
    def __init__(self):
        # Base URLs / KEYs to use in API CALLS
        self.RECIPE_URL = "https://www.themealdb.com/api/json/v1/1/search.php"
        self.API_KEY = ("X-Api-Key", "RyiqF46YrCwIZ8g6iEI3ZQ==79NePNZa9Kz92ewo")
        self.INGREDIENTS_URL = "https://www.themealdb.com/api/json/v1/1/list.php?i=list"
    
    def make_api_call(self, BASE_URL, resource, method, payload=None, content_type=None, API_KEY: tuple = None):
        '''
        This method will make calls to REST APIs
        param BASE_URL: base URL (without anything else) of the API
        param resource: extra parameters added to the API URL (e.g. ?=list)
        param method: e.g. "GET"
        returns: whatever the API shits out (JSON / LIST / DICT)
        '''
        url = BASE_URL + resource
        headers = {}

        # If there is a content_type defined, add it to the header
        if content_type:  
            headers["Content Type"] = content_type

        # If an API key is needed add it to the header. Tuple in format (name, key)
        if API_KEY:  
            headers[API_KEY[0]] = API_KEY[1]

        print(f"Trying {method} {url}")

        # try the API call with all the parameters established
        try:
            response = requests.request(method, url, headers=headers, data=payload)
            print(f"Status: {response.status_code} {response.reason}")
            response.raise_for_status()

        # API CALL ERROR, will return the error code
        except requests.exceptions.HTTPError as e:
            print(e)
            return None
        except:
            print("Unexpected error")
        # If the response has text content, try to parse it as JSON and return the result. 
        # If the response doesn’t have any text content (i.e., it’s empty or None), then return None.
        else:
            return response.json() if response.text else None
    
    def lookup_recipe(self, searchTerm):
        '''
        API call to the mealDB API
        param searchTerm: what the user will put in the searchbar, any string
        returns: a LIST with $offset entries, that are all dictionaries
                Dictionaries: {title:"",ingredients:"",servings:"",instructions:""}
                All of the values associated with the keys are strings
        '''
        api_call = self.make_api_call(self.RECIPE_URL, f"?s={searchTerm}", "GET")
        return api_call
            
    def lookup_ingredients(self):
        '''
        API call to the ingredient API, no paramaters needed
        returns: a dictionary with a single key-pair value inside. The key is "meals"
                inside of meals there's a list of 607 ingredient dictionaries.
                Ingredient dictionary: {idIngredient:int,strIngredient:"name","strDescription":"",strType:None}
        '''
    # The description is the longest thing in the world so please parse it out - James
    # Also, I have 0 clue what strType is, poor documentation, let's also parse that out - James
        
        api_call = self.make_api_call(self.INGREDIENTS_URL,"", "GET")
        return api_call
    
    def parse_recipe(self, data):
        '''
        parses the recipes after a search
        param data: data is the information the API gives out, which is a dictionary with a single ["meals"] key
                referencing the key gives out a list of dictionaries, that contain recipe info
        returns: a list of dictionaries of recipes. The dictionaries are in the desired format:
        {name:"",style:"",owner:"",source:"",steps:{"step1":"","step2":""},ingredients:[("ing","amount"),("ing2","amount2")]}
        '''

        parsed_recipes = []
        for i in data["meals"]:
            # Initialize a dictionary in the desired format
            current_recipe = {
                "name":"",
                "style":"",
                "owner":"",
                "source":"",
                "steps": {},
                "ingredients":[]
            }
            # Fill the dictionary with values
            current_recipe["name"] = i["strMeal"]
            current_recipe["style"] = i["strArea"]
            current_recipe["owner"] = "None"
            current_recipe["source"] = i["strSource"]
            
            # We get ingredients and amount in the desired format
            n = 1
            ing_list = []
            while n < 21:
                if i[f"strIngredient{n}"] != "":
                    if i[f"strMeasure{n}"] != "":
                        ing_list.append((i[f"strIngredient{n}"],i[f"strMeasure{n}"]))
                    else:
                        ing_list.append((i[f"strIngredient{n}"],"to taste"))
                else:
                    break
                n+=1
            # Add ingredients in desired format
            current_recipe["ingredients"] = ing_list

            # We parse the explanation text into different steps
            steps = i["strInstructions"].split('\r\n')
            steps_dictionary = {}
            counter_instructions = 1
            for x in steps:
                if x != "":
                    steps_dictionary[f"step{counter_instructions}"] = x
                    counter_instructions+=1
            # Add steps in desired format
            current_recipe["steps"] = steps_dictionary

            # With the recipe complete we append it to the list that we'll eventually return
            parsed_recipes.append(current_recipe)

        # We return a list of dictionaries of recipes in the desired format
        return parsed_recipes
    
    # Function that should be called on the search bar
    def direct_lookup_function(self,search_term):
        '''
        Function used to search recipes
        param search_term: any string
        returns: list of dictionaries of recipes
        '''
        final = []
        try:
            final = self.parse_recipe(self.lookup_recipe(search_term))
            return final
        except:
            return final

class Database:
    def __init__(self):
        '''
        Information necessary to connect to the database
        '''
        self.host = "192.168.9.2"
        self.user = "root"
        self.port = 3369
        self.pwd = "4iqX0rBR2IdLx2udnc8qwcYyGGh1vhPC"
        self.db = "RecipeDB"

    def connect_to_db(self):
        '''
        Connects to the database and establishes a cursor
        '''
        self.con = pymysql.connect(host=self.host,port=self.port,user=self.user,password=self.pwd,db=self.db,
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def is_open(self):
        '''
        Checks if the connection to the database is open.
        returns: true if connected, False if not connected
        '''
        try:
            self.cur.execute("show tables")
            return True
        except:
            return False
        
    def ensure_connection(self):
        '''
        Opens a new connection to the database if it's not connected already
        '''
        if not self.is_open():
            self.connect_to_db()

    def select_all_table(self, table):
        '''
        Performs a "Select * from" query
        param table: name of one of the tables in the database, string
        returns: a list of dictionaries. 
                Each dictionary is an entry in the table. 
                Every key in the dictionary is a column in the table 
        '''
        self.ensure_connection()
        try:
            self.cur.execute(f"Select * from {table}")
            #gonna get all tuples that satisfy that query
            result = self.cur.fetchall()

        except:
            print("Unexpected error")

        finally:
            #close the connection | we're in a limited environment with only
            #a few limited connections. Anyway, it's important regardless
            self.con.close()

        return result
    
    def select_one_column_table(self, table, column):
        '''
        Prints the column of a table
        param table: the name of the table
        param column: the name of a column in the table
        returns: a list of dictionaries. Dictionaries have a single key: name of the column
        '''
        self.ensure_connection()
        try:
            self.cur.execute(f"Select {column} from {table}")
            #gonna get all tuples that satisfy that query
            result = self.cur.fetchall()
        
        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]
        
        except:
            print("Unexpected error")

        finally:
            #close the connection | we're in a limited environment with only
            #a few limited connections. Anyway, it's important regardless
            self.con.close()

        return result

    def insert_one(self, params, value, table):
        '''
        Inserts a new row into a table in the database
        param param: the names of the column
        param values: the value of what we're about to insert

        !!! this function only works if it's only inserting in 1 column !!! 

        returns: "OK" if it was successful, otherwise the appropiate error message
        '''
        self.ensure_connection()
        try:
            self.cur.execute(f"INSERT INTO {table} ({params}) VALUES ('{value}')")
            self.con.commit()

        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]
        except:
            print("Unexpected error")

        finally:
            self.con.close()

        return "OK"
    
    def insert_user(self,values):
        '''
        function used to insert users into the user table
        param values: should receive a tuple in the format of ("username","email")
        returns: "OK" if it was successful, otherwise the appropiate error message
        '''
        self.ensure_connection()

        try:
            self.cur.execute("INSERT INTO User (Username,Email) VALUES (%s,%s)",values)
            self.con.commit()

        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]
        except:
            print("Unexpected error")

        finally:
            self.con.close()

        return "OK"

    def insert_recipe(self,recipe,username="None"):
        '''
        inserts a recipe in the recipe table, and then fills out the RecNeeds table with the necessary ingredients
        param recipe: single dictionary of the recipe in the specified format
        param username: string with the username - used for recipe owner
        returns: "OK" if it was successful, otherwise the appropiate error message
        '''
        self.ensure_connection()
        #if the current owner of the recipe in the dictionary and owner insert differ
        if recipe["owner"] != username:
            #if the owner inside the dictionary is None, it must be replaced with the actual onwer
            if recipe["owner"] == "None":
                recipe["owner"] = username

        #formatting and quering the recipe table
        repice_table_values = (recipe["name"], recipe["owner"], recipe["style"], json.dumps(recipe["steps"]), recipe["source"])
        try:
            self.cur.execute("INSERT INTO Recipes (RecName, Owner, Style, Steps, Source) VALUES (%s,%s,%s,%s,%s)",repice_table_values)
            self.con.commit()
        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]

        # List to store the necessary IDs to add to RecNeeds tables
        for dif_ingredients in recipe["ingredients"]:
            recneeds_values_list = []
            try:
                recipe_name = recipe["name"]
                self.cur.execute(f"Select RecID from Recipes where RecName = '{recipe_name}'")
                result = self.cur.fetchall()
                recneeds_values_list.append(str(result[0]["RecID"]))
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")

            try:
                ingredient_name = dif_ingredients[0]
                self.cur.execute(f"Select IngID from Ingredients where IngName = '{ingredient_name}'")
                result2 = self.cur.fetchall()
                recneeds_values_list.append(str(result2[0]["IngID"]))
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")

            recneeds_values_list.append(dif_ingredients[1])
            try:
                ingredient_table_values = tuple(recneeds_values_list) 
                #print(ingredient_table_values) # Print created for testing purposes
                self.cur.execute("INSERT INTO RecNeeds (RecID, IngID, Amount) VALUES (%s, %s, %s)",ingredient_table_values)
                self.con.commit()
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")

        try:
            pass
        finally:
            self.con.close()
        return "OK"

    def check_in_others_menus(self,recipe,username="None"):
        '''
        This function checks if the recipe is in other people's menus
        param recipe: string of the recipe name
        param username: string that indicates the name of the user who wants to do a certain action
        returns: True if it is in someone else's menu, False if not.
        '''
        self.ensure_connection()
        if username == "None":
            try:
                self.cur.execute(f"Select * from MenuTemp left join Recipes on MenuTemp.RecID = Recipes.RecID where RecName = '{recipe}';")
                result = self.cur.fetchall()
                if result == ():
                    return False # Not in anyone else's menu, can be easily removed.
                else:
                    return True # In someone else's table - may need to reconsider
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")
            finally:
                self.con.close()
        else:
            try:
                self.cur.execute(f"Select User.UserID,User.Username from User join (select Recipes.RecID,RecName,UserID from MenuTemp left join Recipes on MenuTemp.RecID = Recipes.RecID where RecName = '{recipe}') as X on User.UserID = X.UserID where User.Username != '{username}'")
                result = self.cur.fetchall()
                if result == ():
                    return False # Not in anyone else's menu, can be easily removed.
                else:
                    return True # In someone else's table - may need to reconsider
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")
            finally:
                self.con.close()

    def check_in_others_saved(self,recipe,username="None"):
        '''
        This function checks if the recipe is in other people's Saved Recipes list (bookmarked)
        param recipe: string of the recipe name
        param username: string that indicates the name of the user who wants to do a certain action
        '''
        self.ensure_connection()
        if username == "None":
            UserID = None
        # Get User ID
        else:
            try:
                self.cur.execute(f"Select UserID from User where username = '{username}'")
                result = self.cur.fetchall()
                UserID = str(result[0]["UserID"])
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")
        # Get Recipe ID
        try:
            self.cur.execute(f"Select RecID from Recipes where RecName = '{recipe}'")
            result2 = self.cur.fetchall()
            RecID = str(result2[0]["RecID"])
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
        except:
            print("Unexpected error")

        if username != "None":
            try:
                self.cur.execute(f"Select * from SavedRec where RecID = {RecID} and UserID != {UserID}")
                result = self.cur.fetchall()
                if result == ():
                    return False # Not in anyone else's menu, can be easily removed.
                else:
                    return True # In someone else's table - may need to reconsider
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")
            finally:
                self.con.close()
        else:
            try:
                self.cur.execute(f"Select * from SavedRec where RecID = {RecID}")
                result = self.cur.fetchall()
                if result == ():
                    return False # Not in anyone else's menu, can be easily removed.
                else:
                    return True # In someone else's table - may need to reconsider
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Unexpected error")
            finally:
                self.con.close()

    def check_others_all(self,recipe,username="None"):
        # If it's not in others menus or in others saved recipes it returns False
        if not self.check_in_others_menus(recipe,username) and not self.check_in_others_saved(recipe,username):
            return False
        # otherwise it returns True
        else:
            return True
        
    def delete_recipe(self, RecName="None"):
        '''
        This function permanently deletes a recipe from all tables in the database
        param RecName: string with the recipe name
        '''
        self.ensure_connection()
        if RecName == "None":
            RecID = None
        # Get Recipe ID
        else:
            try:
                self.cur.execute(f"Select RecID from Recipes where RecName = '{RecName}'")
                result = self.cur.fetchall()
                RecID = str(result[0]["RecID"])
            except pymysql.Error as e:
                self.con.rollback()
                RecID = None
                print("Error: " + e.args[1])
            except:
                RecID = None
                print("Unexpected error")
        # Now it deletes from all necessary tables
        self.delete_with_id("RecNeeds","RecID",RecID)
        self.delete_with_id("MenuTemp","RecID",RecID)
        self.delete_with_id("SavedRec","RecID",RecID)
        self.delete_with_id("Recipes","RecID",RecID) # This has to be last, after removing all other references
        self.con.close()

    def delete_with_id(self,table_name,what_id,id):
        '''
        Deletes a value from a table referencing an ID
        parm table_name: string of the table name
        param what_id: string of the column name
        param id: id (number) of the value you want to delete 
        '''
        self.ensure_connection()
        try:
            self.cur.execute(f"delete from {table_name} where {what_id} = {id}")
            self.con.commit()
        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]
        except:
            print("Unexpected error")

    def delete_user(self,username):
        '''
        This function permanently deletes a user from all tables in the database
        param username: string with the username
        (may require password as well, depends on user implementation)
        '''
        self.ensure_connection()
        if username == "None":
            UserID = None
        # Get User ID
        else:
            try:
                self.cur.execute(f"Select UserID from User where username = '{username}'")
                result = self.cur.fetchall()
                UserID = str(result[0]["UserID"])
            except pymysql.Error as e:
                self.con.rollback()
                UserID = None
                print("Error: " + e.args[1])
            except:
                UserID = None
                print("Unexpected error")
        # Now it deletes from all necessary tables
        self.delete_with_id("Allergies","UserID",UserID)
        self.delete_with_id("MenuTemp","UserID",UserID)
        self.delete_with_id("SavedRec","UserID",UserID)
        self.delete_with_id("Owns","UserID",UserID)
        self.delete_with_id("User","UserID",UserID) # This has to be last, after removing all other references
        self.con.close()

    def insert_menu(self,username,recipe,menu_name,description):
        '''
        inserts a single entry in the menu template table
        param username: a string with the username
        param recipe: a string with the recipe name
        param menu_name: a string with the menu the recipe is going to get added to
        param description: a string that indicates the purpose of the recipe in this menu
        returns a tuple: (string of "SUCCESS" or "ERROR", reason)
        '''
        self.ensure_connection()
        if username == "None":
            return ("ERROR","No username specified")
        
        # Get User ID
        else:
            try:
                self.cur.execute(f"Select UserID from User where username = '{username}'")
                result = self.cur.fetchall()
                UserID = str(result[0]["UserID"])
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
                return ("ERROR","Could not find username")
            except:
                print("Unexpected error")
            
        # Get Recipe ID
        try:
            self.cur.execute(f"Select RecID from Recipes where RecName = '{recipe}'")
            result2 = self.cur.fetchall()
            RecID = str(result2[0]["RecID"])
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
            return ("ERROR","Could not find recipe")
        except:
            print("Unexpected error")
        
        # Now that we have the UserID and RecipeID we check if it's a new menu, or adding to an existing one
        try:
            self.cur.execute(f" select * from MenuTemp where MenuName = '{menu_name}' and UserID = {UserID};")
            result3 = self.cur.fetchall()
            # If a menu with that name doesnt exist (it's new), give it a new menu ID
            if result3 == ():
                self.cur.execute(f"select MenuID from MenuTemp order by -MenuID limit 1")
                result4 = self.cur.fetchall()
                MenuID = result4[0]["MenuID"] + 1
            # If a menu with that name does exist, take its menu ID
            else:
                MenuID = str(result3[0]["MenuID"])

        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
            return ("ERROR", "Unexpected error when checking Menu ID")
        except:
            print("Unexpected error")

        # We check to see if there's already an exact same entry on the Menu
        try:
            self.cur.execute(f"select * from MenuTemp where MenuID = {MenuID} and Description = '{description}' and UserID = {UserID} and RecID = {RecID} and MenuName = '{menu_name}';")
            self.con.commit()
            result5 = self.cur.fetchall()
            print(result5)
            if result5 != ():
                return ("ERROR","There's already a copy of this recipe with this description on this menu")
            
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
            return ("ERROR","Unexpected error when checking menus")
        except:
                print("Unexpected error")

        try:
            self.cur.execute(f"insert into MenuTemp (MenuID,Description,UserID,RecID,MenuName) values ({MenuID},'{description}',{UserID},{RecID},'{menu_name}')")
            self.con.commit()
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
            return ("ERROR","Unexpected error when adding recipe to the menu")
        
        self.con.close()
        return ("SUCCESS","You successfully added the recipe to your menu!")

    #Quite honestly, I have no clue what this is. It was created in class
    def query(self,sql):
        self.ensure_connection()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        attrib = [i[0] for i in self.cur.description]
        self.con.close()
        return result, attrib

#################################################
####                                         ####
####        Code for testing purposes        ####
####           Keep commented out            ####
####                                         ####
#################################################

#Delete comments or temporarily copy-paste the code outside
recipe = RecipeAPI()
database = Database()

'''Recipe API Testing Code'''
#test_look = recipe.direct_lookup_function()
#print(test_look)

#thing = recipe.lookup_recipe("soup")
#parsed_info = recipe.parse_recipe(thing)
#for i in parsed_info:
#    print(i)
#    break
#print(thing["meals"])
#print(type(thing["meals"]))

'''Ingredient API Testing Code'''
#ingredients = recipe.lookup_ingredients()
#print(type(ingredients))
#print(ingredients["meals"][0]["strType"])

'''Database Queries Testing Code'''
#print(database.select_all_table("Recipes"))
#print(type(database.select_all_table("Recipes")))
#print(database.select_one_column_table("Recipes", "RecName"))
#print(database.select_one_column_table("Ingredients", "IngName"))
#print(database.insert_one("IngName", "poopies", "Ingredients"))
#print(database.insert_user(("User5","user5@example.com")))
#thing = recipe.direct_lookup_function("pizza")[0]
#print(database.insert_recipe(thing,"James"))
#print(database.check_in_others_menus("Pizza Express Margherita"))
#print(database.check_in_others_saved("Thingy"))
#print(database.check_others_all("Spaghetti Bolognese"))
#database.delete_with_id("Allergies","IngID",1)
#database.delete_user("Poo")
#print(database.insert_menu("User2","Pizza Express Margherita","Others","Snack2"))
database.delete_recipe("Fake Record 3")

#################################################
####                                         ####
####     Ingredients DB Table Management     ####
####                                         ####
#################################################


#Commented code to delete all the entries in the ingredients list 
#you know, in case you f*ck up.... like I did - James
'''
#n should be the smallest ID found on the table
n=0
#final is used to end / break out of the loop !!! BEWARE OF INFINITE LOOPS !!!
final = n + 620
while True:
    database.ensure_connection()
    try:
        database.cur.execute(f"DELETE FROM Ingredients WHERE IngID = {n};")
        database.con.commit()
        #gonna get all tuples that satisfy that query
        result = database.cur.fetchall()
    
    except pymysql.Error as e:
        database.con.rollback()
        print ("Error: " + e.args[1])

    finally:
        #close the connection | we're in a limited environment with only
        #a few limited connections. Anyway, it's important regardless
        database.con.close()

    n+=1
    if n == final:
        break
'''
#Commented code to fill out the ingredients list with ingredients from the database
#left here in case we have to delete everything with code above, and re-fill it
#yes, Im talking from experience, fml - James
'''
for i in ingredients["meals"]:
    database.insert("IngName",i["strIngredient"],"Ingredients")
    print (i["idIngredient"])
    print (i["strIngredient"])
'''

'''Handy commands for testing insert_one, as Ingredients is the easiest one to work with'''
#select * from Ingredients where IngName = "poopies";
#delete from Ingredients where IngName = "poopies";



#Insert command to create test Recipes to delete
'''INSERT INTO Recipes (RecName, Owner, Style, Steps, Source)
    -> VALUES
    ->     ('Fake Record 1', 'John Doe', 'Casual', '{"step1": "Step 1 description", "step2": "Step 2 description"}', 'www.example.com'),
    ->     ('Fake Record 2', 'Jane Smith', 'Formal', '{"step1": "Step 1 description", "step2": "Step 2 description"}', 'www.example.com'),
    ->     ('Fake Record 3', 'Alice Johnson', 'Sporty', '{"step1": "Step 1 description", "step2": "Step 2 description"}', 'www.example.com');
Query OK, 3 rows affected (0.03 sec)'''