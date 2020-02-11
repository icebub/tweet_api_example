import os
import time
import random
import string
from datetime import datetime
import numpy as np

from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_marshmallow import Marshmallow

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.utils import secure_filename

# initialization
app = Flask(__name__)

app.config['SECRET_KEY'] = 'wqereqew'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['UPLOAD_FOLDER'] = "upload"

# extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
auth = HTTPBasicAuth()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user
    
class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    tweet_text = db.Column(db.String(256), index=False)
    img_locate = db.Column(db.String(256), index=False)
    
    
class TweetSchema(ma.ModelSchema):
    class Meta:
        model = Tweet
    
tweet_schema = TweetSchema(many=True)    

@app.route('/api/tweet/submit', methods=['POST'])
@auth.login_required
def submit():
    file = request.files['image']    
    img_locate = ""
    if file and not allowed_file(file.filename):
        return jsonify({"message":"not allowed file type"}) , 400  # not allowed file type
    
    if request.form["use_pic"] == "true" and file and allowed_file(file.filename) :
        filename = secure_filename(file.filename)             
        file_ext = os.path.splitext(filename)[1]
        new_file_name = str(os.path.splitext(filename)[0])+"_"+str(str(time.time()))+"_"+randomString(10)+file_ext  # create new file to prevent duplicate file name

        save_location = os.path.join(app.config['UPLOAD_FOLDER'], new_file_name)
        file.save(save_location)
        img_locate = save_location
    if len(request.form["text"]) > 0 :
        tweet_text = request.form["text"]
        tweet_text = (tweet_text[:250] + '..') if len(tweet_text) > 250 else tweet_text
        tweet = Tweet(tweet_text=tweet_text)
        tweet.user_id = g.user.id
        tweet.img_locate = img_locate
        db.session.add(tweet)
        db.session.commit()
    else :
        return jsonify({"message":"fail no tweet text"}) , 400  # no text
        
    return jsonify({"message":"successful"})


@app.route('/api/tweet/modify/<int:tweet_id>', methods=['POST'])
@auth.login_required
def modify(tweet_id):
    file = request.files['image']    
    img_locate = ""
    if file and not allowed_file(file.filename):
        return jsonify({"message":"not allowed file type"}) , 400  # not allowed file type
    
    if request.form["use_pic"] == "true" and file and allowed_file(file.filename):
        filename = secure_filename(file.filename)        
        file_ext = os.path.splitext(filename)[1]
        new_file_name = str(os.path.splitext(filename)[0])+"_"+str(str(time.time()))+"_"+randomString(10)+file_ext  # create new file to prevent duplicate file name

        save_location = os.path.join(app.config['UPLOAD_FOLDER'], new_file_name)
        file.save(save_location)
        img_locate = save_location
    if len(request.form["text"]) > 0 :
        tweet = Tweet.query.filter_by(id=tweet_id,user_id=g.user.id).first()   
        if tweet is None :
            return jsonify({"message":"fail no tweet post by this user"}) , 400  # no tweet    
        tweet_text = request.form["text"]
        tweet_text = (tweet_text[:250] + '..') if len(tweet_text) > 250 else tweet_text
        tweet.tweet_text = tweet_text
        tweet.user_id = g.user.id     
        
        if request.form["use_pic"] != "true" : # incase user want to delete picture
            tweet.img_locate = ""
        elif img_locate != "" :
            tweet.img_locate = img_locate
        
        db.session.commit()
    else :
        return jsonify({"message":"fail no tweet text"}) , 400  # no text      
    return jsonify({"message":"successful"})


@app.route('/api/tweet/search/<string:text>/<int:limit>', methods=['GET',"POST"])
def search(text,limit=5):   
    limit = np.clip(limit,1,10) 
    tweet = Tweet.query.filter(Tweet.tweet_text.ilike("%"+str(text)+"%")).order_by(Tweet.pub_date.desc()).limit(limit)
    return jsonify({"data":tweet_schema.dump(tweet.all())})


@app.route('/api/tweet/user/<string:username>/<int:limit>', methods=['GET',"POST"])
def getTweet(username,limit=5):      
    limit = np.clip(limit,1,10)
    tweet = Tweet.query.join(User,User.id==Tweet.user_id).filter_by(username=username).order_by(Tweet.pub_date.desc()).limit(limit)    
    return jsonify({"data":tweet_schema.dump(tweet.all())})


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({"message":"missing arguments"}) , 400    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"message":"username exist"}) , 400     # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username,"message":"successful"}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)