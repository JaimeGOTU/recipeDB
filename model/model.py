import requests
import json
import pymysql

class RecipeAPI:
    def __init__(self):
        # Base URLs
        self.RECIPE_URL = "https://api.api-ninjas.com/v1/recipe"
        self.API_KEY = ("X-Api-Key", "RyiqF46YrCwIZ8g6iEI3ZQ==79NePNZa9Kz92ewo")
    
    def make_api_call(self, BASE_URL, resource, method, payload=None, content_type=None, API_KEY: tuple = None):
        #This method will make calls to REST APIs
        url = BASE_URL + resource
        headers = {}
        if content_type:  # If there is a content_type defined
            headers["Content Type"] = content_type

        if API_KEY:  # If an API key is needed. Tuple in format (name, key)
            headers[API_KEY[0]] = API_KEY[1]

        print(f"Trying {method} {url}")

        try:
            response = requests.request(method, url, headers=headers, data=payload)
            print(f"Status: {response.status_code} {response.reason}")
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            return None
        else:
            return response.json() if response.text else None
    
    def lookup_recipe(self, searchTerm, offset=10):
        api_call = self.make_api_call(self.RECIPE_URL, f"?query={searchTerm}&offset={offset}", "GET", API_KEY=self.API_KEY)
        return api_call

class Database:
    def __init__(self):
        self.host = "192.168.9.2"
        self.user = "root"
        self.port = 3369
        self.pwd = "4iqX0rBR2IdLx2udnc8qwcYyGGh1vhPC"
        self.db = "RecipeDB"

    def connect_to_db(self):
        self.con = pymysql.connect(host=self.host,port=self.port,user=self.user,password=self.pwd,db=self.db,
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def is_open(self):
        try:
            self.cur.execute("show tables")
            return True
        except:
            return False
        
    def ensure_connection(self):
        if not self.is_open():
            self.connect_to_db()

    def select_all_table(self, table):
        self.ensure_connection()
        try:
            self.cur.execute(f"Select * from {table}")
            #gonna get all tuples that satisfy that query
            result = self.cur.fetchall()

        finally:
            #close the connection | we're in a limited environment with only
            #a few limited connections. Anyway, it's important regardless
            self.con.close()

        return result
    
    def select_one_table(self, table, column):
        self.ensure_connection()
        try:
            self.cur.execute(f"Select {column} from {table}")
            #gonna get all tuples that satisfy that query
            result = self.cur.fetchall()
        
        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]

        finally:
            #close the connection | we're in a limited environment with only
            #a few limited connections. Anyway, it's important regardless
            self.con.close()

        return result

    def insert(self, params, values, table):
        self.ensure_connection()
        try:
            self.cur.execute(f"INSERT INTO {table} ({params}) VALUES ('{values}')")
            self.con.commit()

        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]

        finally:
            self.con.close()

        return "OK"

    def query(self,sql):
        self.ensure_connection()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        attrib = [i[0] for i in self.cur.description]
        self.con.close()
        return result, attrib

#recipe = RecipeAPI()
#print(recipe.lookup_recipe("Pizza"))

database = Database()
#print(database.select_all_table("Recipes"))
#print(database.select_one_table("Recipes", "Steps"))

print(database.insert("IngName", "Tomato", "Ingredients"))
print(database.select_one_table("Ingredients", "IngName"))