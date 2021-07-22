from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
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
    email = db.Column(db.String(100))
    password = db.Column(db.String(6))


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
@app.route('/user',methods= ['POST'])
def add_user():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    new_user = User(name,email,password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user)

# get users
app.route('/users',methods = ['GET'])
def get_user():
    all_users = User.query.all()
    return jsonify(all_users)

# run server
if __name__ == '__main__':
    app.run(debug=True)



