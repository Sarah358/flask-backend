from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import sqlite3
import os

# init app
app = Flask(__name__)

# @app.route('/', methods= ['GET'])
# def get():
#     return jsonify ({"msg": "Hello World"})
    
# setting sqlalchemy db uri
basedir = os.path.abspath(os.path.dirname(__file__))

# setting up db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db
db = SQLAlchemy(app)

# init marshmallow
ma = Marshmallow(app)

# user model
class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100),unique = True)
    password = db.Column(db.String(6),unique = True)


# constructor
    def __init__(self,name,email,password):
        self.name = name
        self.email = email
        self.password = password

# user shema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','name','email','password')

# init schema
# user_schema = UserSchema(strict = True)
# users_schema = UserSchema(many = True, strict = True)

# create a user
@app.route('/users',methods= ['POST'])
def add_user():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    conn = sqlite3.connect('db.sqlite')
    conn_db = conn.cursor()
    conn_db.execute("SELECT * FROM user where email = ? OR password = ?;",(email,password))
    record = conn_db.fetchall()
    if(len(record) == 0):
        new_user = User(name,email,password)
        db.session.add(new_user)
        db.session.commit()

        response ='User account created'
        return response
    else:
        response = "User details already exists"
        return response


# get users
@app.route('/users',methods = ['GET'])
def get_user():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['email'] = user.email
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({"users":output})


# run server
if __name__ == '__main__':
    app.run(debug=True)



