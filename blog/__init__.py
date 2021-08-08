from flask import Flask

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'da43bc5f4d53dd8903a3b4bf972ed09f8e244e44e0b27d92'
# app.config[
# 'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c1993394:Cy381391222@csmysql.cs.cf.ac.uk:3306/c1993394_CMT120_practice'
app.config.from_object(Config)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from blog import routes

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from blog.models import User, Post, Comment, Rate, Taglist, Tags
from blog.views import AdminView

admin = Admin(app, name='Admin', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Rate, db.session))
admin.add_view(ModelView(Taglist, db.session))
admin.add_view(ModelView(Tags, db.session))
