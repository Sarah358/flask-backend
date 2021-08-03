from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import sqlite3
import uuid
import datetime
import os
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash

# init app
app = Flask(__name__)

# Setup the secret-key
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY') # Change this!



    

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
    password = db.Column(db.String(20),unique = True)


    # constructor
    def __init__(self,name,email,password):
        self.name = name
        self.email = email
        self.password = password

# creating decorator to work with access token
def token_required(f):
    @wraps(f)
    # pass positional arguments and keyword arguments
    def decorated(*args,**kwargs):
        token = None

        # pass token in the header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message':'Token is missing'}),401
        # try catch errors
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id= data['id'] ).first()
        except:
            return jsonify({'message':'Token is invalid'}),401
        # pass user object to the route
        return f(current_user, *args,**kwargs)
    # return decorated fuunction
    return decorated


# create a user
@app.route('/user',methods= ['POST'])
# passing the decorator
@token_required
def add_user(current_user):
    data = request.get_json()
    hashed_password = generate_password_hash(data.get('password'), method='sha256')
    new_user = User(name=data.get('name'),email=data.get('email'), password=hashed_password)       
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201
  
   

# get users
@app.route('/user',methods = ['GET'])
@token_required
def get_user(current_user):
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

# get one user
@app.route('/user/<id>',methods =['GET'])
@token_required

def get_one_user(current_user,id):
    user = User.query.filter_by(id = id).first()

    if not user:
        return jsonify ({'message':'No user found'})
    
    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['email'] = user.email
    user_data['password'] = user.password
    
    return jsonify ({'user':user_data})

# edit user
@app.route('/user/<id>',methods = ['PUT'])
def edit_user(id):
    return ''

# delete user
@app.route('/user/<id>',methods = ['DELETE'])
@token_required
def delete_user(current_user,id):
    user = User.query.filter_by(id = id).first()
    if not user:
        return jsonify ({'message':'No user found'})
    db.session.delete(user)
    db.session.commit()

    return jsonify ({'message':'user deleted'})


# login
@app.route('/login')


def login():
    # authentication
    auth = request.authorization
    # check for authentication before logging in
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify',401,{'WWW-Authenticate':'Basic realm = "login required"'})

    # query user
    user = User.query.filter_by(name = auth.username).first()

    if not user:
        return jsonify ({'message':'no user found'})
    if check_password_hash(user.password,auth.password):
        # encode the token in the secret key
        token = jwt.encode({'id':user.id,'exp': datetime.datetime.utcnow() +datetime.timedelta(minutes = 30)},app.config['SECRET_KEY'])
        
        return jsonify ({'token':token}),200
    return make_response('could not verify password',401,{'WWW-Authenticate':'Basic realm = "login required"'})




# run server
if __name__ == '__main__':
    app.run(debug=True)



