
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request
import pymysql

app = Flask(__name__, template_folder="templates")

#Separate file and then import could be better for Final project
#Credentials 100% on a different file!!!!
##################### DATABASE CLASS ##########################################

class Database:
    def __init__(self):
        host = "JaimeGOTU.mysql.pythonanywhere-services.com"
        user = "JaimeGOTU"
        pwd = "cisco123"
        db = "JaimeGOTU$tabletable"

        self.con = pymysql.connect(host=host,user=user,password=pwd,db=db,
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def select(self):
        try:
            self.cur.execute("Select * from Student")
            #gonna get all tuples that satisfy that query
            result = self.cur.fetchall()

        finally:
            #close the connection | we're in a limited environment with only
            #a few limited connections. Anyway, it's important regardless
            self.con.close()

        return result

    def insert(self, id, name, grade):
        try:
            self.cur.execute("insert into Student (id, name, grade) values (%s, %s, %s)", (id,name, grade))
            self.con.commit()

        except pymysql.Error as e:
            self.con.rollback()
            return "Error: " + e.args[1]

        finally:
            self.con.close()

        return "OK"

    def query(self,sql):
        self.cur.execute(sql)
        result = self.cur.fetchall()
        attrib = [i[0] for i in self.cur.description]
        self.con.close()

        return result, attrib


####################### FLASK STUFF ##########################################
@app.route('/')
def hello_world():
    #variable to pass to the html
    myvar = 'INFR3810'
    #when there's a request, the URL it will render this file (webpage) - return
    #this is how we pass variables to html
    return render_template("index.html", msg=myvar)

@app.route('/list')
def list_function():
    db = Database()
    result = db.select()
    return render_template("results.html", result=result)


    if request.method=="POST":
        data = request.form
        name = data['name']

#post is technically safer | if you want to bookmark, use GET, maintains params.
@app.route('/insert', methods=['GET', 'POST'])
def insert():
    msg = ""
    #so after user clicks submit it will render this
    if request.method=="POST":
        data = request.form
        id = data['id']
        name = data['name']
        grade = data['grade']

        db = Database()
        msg = db.insert(id, name, grade)

    #first it renders the form, it's loaded
    #and then it executes again and gets the name
    return render_template('form.html', msg=msg)


@app.route('/query', methods=['GET', 'POST'])
def query():
    result=None
    attrib=None
    #so after user clicks submit it will render this
    if request.method=="POST":
        data = request.form
        sql = data['sql']

        db = Database()
        result , attrib = db.query(sql)

    #first it renders the form, it's loaded
    #and then it executes again and gets the name
    return render_template('query.html', result=result,attrib=attrib)


@app.route('/example')
def example_function():
    return "<h1>This is my example function</h1>"