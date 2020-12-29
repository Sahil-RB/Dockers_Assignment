from flask import Flask, render_template, redirect, url_for, request,make_response
import mysql.connector
import socket
import os
import json
import time
time.sleep(30)

app = Flask(__name__)

TEXT1=os.environ.get('TEXT1', "Hackfest")
TEXT2=os.environ.get('TEXT2', "Registration")
ORGANIZER=os.environ.get('ORGANIZER', "UVCE")


mydb = mysql.connector.connect(user='admin', password='admin',
                              host='db', database='RSVP',
                              auth_plugin='mysql_native_password')



mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS rsvpdata (_id int(100) NOT NULL AUTO_INCREMENT,name varchar(100) NOT NULL,email varchar(100) NOT NULL,PRIMARY KEY (_id)) ;")
mycursor.close()
class RSVP(object):
    """Simple Model class for RSVP"""
    def __init__(self, name, email, _id=None):
        self.name = name
        self.email = email
        self._id = _id

    def dict(self):
        _id = str(self._id)
        return {
            "_id": _id,
            "name": self.name,
            "email": self.email,
            "links": {
                "self": "{}api/rsvps/{}".format(request.url_root, _id)
            }
        }

    def delete(self):
        mycursor = mydb.cursor()
        query = "DELETE FROM rsvpdata WHERE id = "+self._id
        mycursor.execute(query)
        mydb.commit()
        mycursor.close()
        

    @staticmethod
    def find_all():
        mycursor = mydb.cursor()
        query = "SELECT * FROM rsvpdata"
        mycursor.execute(query)
        myresult = mycursor.fetchall()
        mycursor.close()
        for doc in myresult:
            return(RSVP(**doc))
        

    @staticmethod
    def find_one(id):
        mycursor = mydb.cursor()
        query  = "SELECT * FROM rsvpdata WHERE _id = "
        mycursor.execute(query)
        myresult = mycursor.fetchone()
        mycursor.close()
        return myresult and RSVP(myresult['name'], myresult['email'], myresult['_id'])

    @staticmethod
    def new(name, email):
        doc = {"name": name, "email": email}
        mycursor = mydb.cursor()
        query = "INSERT INTO rsvpdata (name, email) VALUES (%s, %s)"
        arg = (name, email)
        mycursor.execute(query, arg)
        mydb.commit()
        mycursor.close()
        return RSVP(name, email, mycursor.lastrowid)

@app.route('/')
def rsvp():
    mycursor = mydb.cursor()
    query = "SELECT name, email FROM rsvpdata"
    mycursor.execute(query)
    _items = mycursor.fetchall()
    mycursor.close()
    items = [item for item in _items]
    print(items)
    count = len(items)
    hostname = socket.gethostname()
    return render_template('profile.html', counter=count, hostname=hostname,\
                           items=items, TEXT1=TEXT1, TEXT2=TEXT2, ORGANIZER=ORGANIZER)

@app.route('/new', methods=['POST'])
def new():
    mycursor = mydb.cursor()
    query = "INSERT INTO rsvpdata (name, email) VALUES (%s, %s)"
    args = (request.form['name'], request.form['email'])
    mycursor.execute(query, args)
    mycursor.close()
    mydb.commit()
    return redirect(url_for('rsvp'))

@app.route('/api/rsvps', methods=['GET', 'POST'])
def api_rsvps():
    if request.method == 'GET':
        docs = [rsvp.dict() for rsvp in RSVP.find_all()]
        return json.dumps(docs, indent=True)
    else:
        try:
            doc = json.loads(request.data)
        except ValueError:
            return '{"error": "expecting JSON payload"}', 400

        if 'name' not in doc:
            return '{"error": "name field is missing"}', 400
        if 'email' not in doc:
            return '{"error": "email field is missing"}', 400

        rsvp = RSVP.new(name=doc['name'], email=doc['email'])
        return json.dumps(rsvp.dict(), indent=True)

@app.route('/api/rsvps/<id>', methods=['GET', 'DELETE'])
def api_rsvp(id):
    rsvp = RSVP.find_one(id)
    if not rsvp:
        return json.dumps({"error": "not found"}), 404

    if request.method == 'GET':
        return json.dumps(rsvp.dict(), indent=True)
    elif request.method == 'DELETE':
        rsvp.delete()
        return json.dumps({"deleted": "true"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
