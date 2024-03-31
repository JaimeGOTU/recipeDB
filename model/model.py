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
            print("API CALL ERROR (line 44)")
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
        try:
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
        except:
            return []
    
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
    
    def get_youtubelink_parser(self,recipe_name):
        '''
        function to get the youtube link of a recipe given it's name
        params recipe_name: str of the full recipe name
        '''
        try:
            youtube_link = self.lookup_recipe(recipe_name)["meals"][0]["strYoutube"]
            # Convert the YouTube link into the embeddable format
            youtube_link = youtube_link.replace('watch?v=', 'embed/')
            return youtube_link
        except:
            return None

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
            print("SELECT * FROM TABLE ERROR (line 200)")

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
            print("SELECT COLUMN FROM TABLE ERROR (line 227)")

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
            print("INSERT INTO TABLE ERROR (line 255)")

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
            print("INSERT INTO USER ERROR (line 278)")

        finally:
            self.con.close()

        return "OK"

    def insert_recipe(self,recipe,username="None"):
        '''
        inserts a recipe in the recipe table, and then fills out the RecNeeds table with the necessary ingredients
        param recipe: single dictionary of the recipe in the specified format
        param username: string with the username - used for recipe owner
        returns: "OK" if it was successful, otherwise the appropiate error message

        SPECIFIED FORMAT: {'RecID':"str","style":"str","owner":"str","source":"str,
        "steps":JSON,"ingredients":[("strIng","strAmount),("strIng","strAmount)...]}
        '''

        #print(recipe)

        self.ensure_connection()
        #formatting and quering the recipe table
        repice_table_values = (recipe["name"], username, recipe["style"], json.dumps(recipe["steps"]), recipe["source"])
        try:
            self.cur.execute("INSERT INTO Recipes (RecName, Owner, Style, Steps, Source) VALUES (%s,%s,%s,%s,%s)",repice_table_values)
            self.con.commit()
        except pymysql.Error as e:
            self.con.rollback()
            print("Error:" + e.args[1])
            return "Error: " + e.args[1]
        except:
            print("Unexpected error")

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
                print("SELECT RECID FROM RECIPES ERROR (line 320)")

            try:
                ingredient_name = dif_ingredients[0]
                self.cur.execute(f"Select IngID from Ingredients where IngName = '{ingredient_name}'")
                result2 = self.cur.fetchall()
                recneeds_values_list.append(str(result2[0]["IngID"]))
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("SELECT INGID FROM INGREDIENTS ERROR (line 331)")

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
                print("INSERT INTO RECNEEDS ERROR (line 343)")

        try:
            if username == "None":
                pass
            else:
                SavedRec_Values = []
                try:
                    User_Name = username
                    self.cur.execute(f"select UserID from User where Username = '{User_Name}'")
                    resultU = self.cur.fetchall()
                    SavedRec_Values.append(str(resultU[0]["UserID"]))
                except:
                    print("SELECT USERID FROM USER ERROR (line 356)")

                try:
                    recipe_name = recipe["name"]
                    self.cur.execute(f"select RecID from Recipes where RecName = '{recipe_name}'")
                    resultR = self.cur.fetchall()
                    SavedRec_Values.append(str(resultR[0]["RecID"]))
                except:
                    print("SELECT RECID FROM RECIPES ERROR (line 364)")

                try:
                    self.cur.execute("INSERT INTO SavedRec (UserID, RecID) VALUES (%s, %s)",SavedRec_Values)
                    self.con.commit()

                except:
                    print("INSERT INTO SAVED REC ERROR (line 371)")


            
            
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
                print("SELECT * FROM MENUTEMP ERROR (line 400)")
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
                print("SELECT USER.USERID, USER.USERNAME FROM USER ERROR (line 415)")
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
                print("SELECT USERID FROM USER ERROR (line 438)")
        # Get Recipe ID
        try:
            self.cur.execute(f"Select RecID from Recipes where RecName = '{recipe}'")
            result2 = self.cur.fetchall()
            RecID = str(result2[0]["RecID"])
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
        except:
            print("SELECT RECID FROM RECIPES (lines 448)")

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
                print("SELECT * FROM SAVEDREC (line 462)")
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
                print("SELECT * FROM SAVED REC (line 477)")
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
                print("SELECT RECID FROM RECIPES (line 509)")
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
            print("DELETE FROM TABLE ERROR (line 532)")

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
                print("SELECT USERID FROM USER ERROR (line 555)")
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
                print("SELECT USERID FROM USER ERROR (line 588)")
            finally:
                self.con.close()
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
            print("SELECT RECID FROM RECIPES ERROR (line 601)")
        finally:
            self.con.close()
        
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
            print("SELECT * FROM MENUTEMP ERROR (line 623)")

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
                print("SELECT * FROM MENU TEMP ERROR (line 639)")

        try:
            self.cur.execute(f"insert into MenuTemp (MenuID,Description,UserID,RecID,MenuName) values ({MenuID},'{description}',{UserID},{RecID},'{menu_name}')")
            self.con.commit()
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
            return ("ERROR","Unexpected error when adding recipe to the menu")
        
        self.con.close()
        return ("SUCCESS","You successfully added the recipe to your menu!")

    def random_recipes(self,amount):
        '''
        Gets "amount" amount of random recipes
        returns a list of dictionaries. Each dictionary is a recipe.
        The keys are the column names (RecID, RecMame,Owner,Style,Steps,Source)
        '''
        amount = str(amount)
        self.ensure_connection()
        try:
            self.cur.execute(f"select distinct * from Recipes order by RAND() limit {amount}")
            result = self.cur.fetchall()
            return result
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
        #except:
        #    print("Unexpected error")
        self.con.close()

    def get_ingredients(self,recipe):
        '''
        returns a dictionary of {"ingredient":"amount"} for a given recipe
        params recipe: str of the recipe name
        '''
        self.ensure_connection()
        # Get Recipe ID
        try:
            self.cur.execute(f"Select RecID from Recipes where RecName = '{recipe}';")
            result2 = self.cur.fetchall()
            RecID = str(result2[0]["RecID"])
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
        except:
            print("SELECT RECID FROM RECIPES ERROR (line 686)")
        
        ingredient_dict = {}

        try:
            self.cur.execute(f"select IngName,Amount from RecNeeds left join Ingredients on RecNeeds.IngID = Ingredients.IngID where RecID = {RecID};")
            result3 = self.cur.fetchall()
            for i in result3:
                ingredient_dict[i["IngName"]] = i["Amount"]
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
        except:
            print("SELECT INGNAME, AMOUNT FROM RECNEEDS ERROR (line 699)")
        
        if ingredient_dict == {}:
            return {"Could not load":"ERROR"}
        else:
            return(ingredient_dict)

    def update_recipe(self,recipe,username="None"):
        '''
        updates a recipe in the recipe table, 
        and then (hopefully) the other tables have no issues
        param recipe: single dictionary of the recipe in the specified format
        param username: string with the username - used for recipe owner
        returns: "OK" if it was successful, otherwise the appropiate error message

        SPECIFIED FORMAT: {'RecID':"str","style":"str","owner":"str","source":"str,
        "steps":JSON,"ingredients":[("strIng","strAmount),("strIng","strAmount)...]}
        '''
        self.ensure_connection()
        if username == "None":
            print("No username, cannot update")
        else:
            try:
                self.cur.execute(f"select RecID from Recipes where RecName = '{recipe['name']}'")
                result_RecID = self.cur.fetchall()
                RecID = result_RecID[0]["RecID"]
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("Error at RecID lvl (line 732)")
            
            Update_table_values = (recipe["name"], recipe["style"], json.dumps(recipe["steps"]), recipe["source"], RecID, username)
            try:
                self.cur.execute("UPDATE Recipes SET RecName = %s, Style = %s, Steps = %s, Source = %s WHERE RecID = %s AND Owner = %s", Update_table_values)
                self.con.commit()
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("UPDATE RECIPES ERROR (line 742)")

    def add_from_others(self, recipe, username):
        self.ensure_connection()
        try:
            if username == "None":
                pass
            else:
                Saved_Other_Values = []
                try:
                    User_Name = username
                    self.cur.execute(f"select UserID from User where Username = '{User_Name}'")
                    resultUser = self.cur.fetchall()
                    Saved_Other_Values.append(str(resultUser[0]["UserID"]))
                except:
                    print("SELECT USERID FROM USER ERROR (line 757)")

                try:
                    recipe_name = recipe
                    self.cur.execute(f"select RecID, Owner from Recipes where RecName = '{recipe_name}'")
                    resultRec = self.cur.fetchall()
                    Saved_Other_Values.append(str(resultRec[0]["RecID"]))
                    Saved_Owner_name = resultRec[0]["Owner"]
                except:
                    print("SELECT RECID FROM RECIPES ERROR (line 766)")

                try:
                    if Saved_Owner_name == username:
                        print("Owner Already Added")
                        return "Owner Already Added"
                        
                    else:
                        self.cur.execute(f"SELECT * from SavedRec Where UserID = {resultUser[0]['UserID']} and RecID = {resultRec[0]['RecID']}")
                        ReturnUserRec = self.cur.fetchall()
                        if ReturnUserRec == ():                            
                            self.cur.execute("INSERT INTO SavedRec (UserID, RecID) VALUES (%s, %s)",Saved_Other_Values)
                            self.con.commit()
                        else:
                            print("User Already Added Recipe")
                            return "User Already Added Recipe"
                except pymysql.Error as e:
                    self.con.rollback()
                    print("Error: " + e.args[1])
                except:
                    print("INSERT INTO SAVED REC ERROR (line 784)")
        except:
            print("Error ADD_FROM_OTHER")

######### DO #########
#UPDATE Recipes  SET RecName = 'New Recipe Name', Owner = 'New Owner', Style = 'New Style', Steps = '{"step1": "New Step 1", "step2": "New Step 2"}', Source = 'New Source' WHERE RecID = 1;


####### DO #######
#Also for ingredients but i gotta figure that out later

        pass

    def browse_main_table(self,search_term=""):
        '''
        Looks in the table for a search term, and if it's empty shows all entries
        param search_term: any string. Regex will handle the rest (e.g. eggs)
        returns: a list of dictionaries. 
                Each dictionary is an entry in the table. 
                Every key in the dictionary is a column in the table 
        '''
        self.ensure_connection()
        result=[]
        try:
            self.cur.execute(f"SELECT * FROM Recipes WHERE RecName LIKE IF('{search_term}' = '', '%', CONCAT('%', '{search_term}', '%'));")
            result = self.cur.fetchall()
        except:
            print("SELECT * FROM TABLE ERROR (line 779)")
        finally:
            self.con.close()
        return result

    def show_saved_recipes(self,username="None"):
        '''
        This function returns a list of dictionaries of the recipes of a user given its username
        param username: string of the username
        '''
        self.ensure_connection()
        recipe_id_list = []
        recipes_to_return = []
        if username == "None":
            print("no username error")
            return []
        else:
            UserID = self.get_id("UserID","User","Username",username)
            try:
                self.cur.execute(f"select RecID from SavedRec where UserID = {UserID}")
                recipe_id_list = self.cur.fetchall() # format [{'RecID': 28}, {'RecID': 34}, {'RecID': 25}]
            except pymysql.Error as e:
                self.con.rollback()
                print("Error: " + e.args[1])
            except:
                print("getting recipe id list error")
            
            if recipe_id_list == []:
                print("no saved recipes")
                return []
            else:
                try:
                    for i in recipe_id_list:
                        try:
                            real_value = i["RecID"]
                            self.cur.execute(f"Select * from Recipes where RecID = '{real_value}';")
                            result = self.cur.fetchall()[0]
                            recipes_to_return.append(result)
                        except pymysql.Error as e:
                            self.con.rollback()
                            print("Error: " + e.args[1])
                        except:
                            print("getting recipes error")
                except pymysql.Error as e:
                    self.con.rollback()
                    print("Error: " + e.args[1])
                except:
                    print("getting recipe id list error")

        return recipes_to_return

    def get_id(self,what_id,what_table,what_column,keyword):
        '''
        Gets you an id from a string
        params what_id: select "what_id"
        params what_table: from "what_table"
        params what_column: where "what_column"
        params keyword: = "keyword"
        returns an int with the ID
        '''
        self.ensure_connection()
        # Get Recipe ID
        try:
            self.cur.execute(f"Select {what_id} from {what_table} where {what_column} = '{keyword}';")
            result = self.cur.fetchall()
            RecID = str(result[0][f"{what_id}"])
            return RecID
        except pymysql.Error as e:
            self.con.rollback()
            print("Error: " + e.args[1])
        except:
            print("SELECT id from get_id function error")
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
#print(recipe.get_youtubelink_parser("Chicken Curry"))

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
#database.delete_recipe("Fake Record 3")
#print(database.random_recipes(2))
#print(database.get_ingredients("Pizza Express Margherita"))
#print(database.browse_main_table("poop"))
#print(database.get_id("RecID","Recipes","RecName","Poop pie"))
#print(database.show_saved_recipes("rpazzi"))

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





#Test RecID and UserID into SavedRec

Dummy_data1 = {
    "name":"Never going to give you up Spaghetti",
    "style":"Chinese",
    "owner":"Rick",
    "source":"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "steps": {"step1": "Boil water", "step2": "Cook spaghetti", "step3": "Prepare sauce", "step4": "Combine spaghetti and sauce"},
    "ingredients":[("water","69 ml"),("spaghetti","420gr"),("pasta sauce","269ml")]}


Dummy_Update ={
    "name":"UDPATE RECIPE",
    "style":"Chinese",
    "owner":"rpazzi",
    "source":"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "steps": {"step1": "Boil water", "step2": "Cook spaghetti", "step3": "Prepare sauce", "step4": "Combine spaghetti and sauce"},
    "ingredients":[("water","69 ml"),("spaghetti","420gr"),("pasta sauce","269ml")]} 


#database.insert_recipe(Dummy_data1, 'asdf')
#database.delete_recipe("Dummy_data1")
#database.update_recipe(Dummy_Update, "rpazzi")
#database.add_from_others("Never going to give you up Spaghetti", "trump")
