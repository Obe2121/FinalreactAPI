from flask import Flask, make_response, request, g
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

class Config():
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(email, password):
    u = User.query.filter_by(email=email).first()
    if u is None:
        return False
    g.current_user = u
    return u.check_hashed_password(password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<{self.id}|{self.user_id}>'

    def from_dict(self,data):
        self.id = data['id']
        self.body = data['body']
        self.user_id = data['user_id']

    def to_dict(self):
        return {"user_id": self.user_id, "body":self.body, "id":self.id}

    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    first_name = db.Column(db.String)
    last_name =  db.Column(db.Text)
    password = db.Column(db.String(255))
    post_id = db.Column(db.ForeignKey('post.id'))

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_hashed_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<{self.id}|{self.email}>'

    def from_dict(self, data):
        self.email = data['email']
        self.password = self.hash_password(data['password'])

    def to_dict(self):
        return {"id": self.id, "email": self.email}



@app.get('/login')
@basic_auth.login_required()
def login():
    return make_response(f"valid login for user id: {g.current_user.user_id}", 200)

@app.get('/user')
def get_users():
    return make_response({"users":[user.to_dict() for user in User.query.all()]}, 200)

@app.get('/user/<int:id>')
def get_user(id):
    return make_response(User.query.get(id).to_dict(), 200)

@app.post('/user')
def post_user():
    data = request.get_json()
    new_user = User()
    new_user.from_dict(data)
    new_user.save()
    return make_response("success",200)

@app.put('/user/<int:id>')
def put_user(user_id):
    data = request.get_json()
    user=User.query.get(user_id)
    user.from_dict(data)
    user.save()
    return make_response("success",200)

@app.delete('/user/<int:id>')
def delete_user(id):
    User.query.get(id).delete()
    return make_response("success",200)


@app.get('/post')
def get_post():
    return make_response({"posts":[post.to_dict() for post in Post.query.all()]}, 200)

@app.get('/post/<int:id>')
def get_post(id):
    return make_response(Post.query.get(id).to_dict(), 200)

@app.post('/post')
def post_post():
    data = request.get_json()
    new_post = Post()
    new_post.from_dict(data)
    new_post.save()
    return make_response("success",200)

@app.put('/post/<int:id>')
def put_post(id):
    data = request.get_json()
    post=Post.query.get(id)
    post.from_dict(data)
    post.save()
    return make_response("success",200)

@app.delete('/post/<int:id>')
def delete_post(id):
    Post.query.get(id).delete()
    return make_response("success",200)

@app.get('/post/user/<int:id>')
def get_recipes_by_user_id(id):
    return make_response({"posts":[post.to_dict() for post in User.query.get(id).posts]},200)