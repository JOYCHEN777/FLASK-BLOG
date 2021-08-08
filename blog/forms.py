from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, InputRequired
from blog.models import User, Rate
from flask_login import current_user
from sqlalchemy import or_


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp('^.{6,12}$',
                                                                            message='Your password should be between 6 and 12 characters long.')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password',
                                                                                             message='please make sure you type the same password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exist. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exist. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class CommentForm(FlaskForm):
    comment = StringField('Comment', validators=[InputRequired()])
    submit = SubmitField('Post comment')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = TextAreaField('title', validators=[
        DataRequired(), Length(min=1, max=140)])
    content = TextAreaField('content', validators=[
        DataRequired()])
    submit = SubmitField('Post')


class SearchForm(FlaskForm):
    type = SelectField('search_type', choices=[(1, 'blog title'), (2, 'blog content'), (3, 'all')], default=3,
                       coerce=int)
    info = TextAreaField('search_content', validators=[DataRequired()])
    submit = SubmitField('Search')


class RateForm(FlaskForm):
    rate = SelectField('post_rate', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=5,
                       coerce=int)
    submit = SubmitField('Submit')


class SortForm(FlaskForm):
    sort = SelectField('post_rate', choices=[(0, 'Latest First'), (1, 'Oldest First')], default=0,
                       coerce=int)
    submit = SubmitField('Confirm')
