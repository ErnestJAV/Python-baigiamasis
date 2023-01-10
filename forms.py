from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField,FileField, validators
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional
from flask_login import current_user
import main
from wtforms_sqlalchemy.fields import QuerySelectField


class AddCategory(FlaskForm):
    name = StringField('Category', [DataRequired()])
    description = StringField('Description', [DataRequired()])
    submit = SubmitField('Submit')


class EditCat(FlaskForm):
    name = StringField('Category', [DataRequired()])
    description = StringField('Description', [DataRequired()])
    submit = SubmitField('Submit')


class AddNote(FlaskForm):
    description = StringField('Description', [DataRequired()])
    text = StringField('Text', [DataRequired()])
    submit = SubmitField('Submit')
    groups = QuerySelectField(query_factory=lambda: main.Groups.query.filter_by(userid=current_user.id).all(), get_label='name',  validators=[validators.InputRequired("Please select a group or create a new one.")], label='Category')
    image = FileField('Image', validators=[Optional()])


class SignUpForm(FlaskForm):
    email_address = EmailField('Email Address', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    password1 = PasswordField('Password', [DataRequired()])
    password2 = PasswordField('Password confirm', [DataRequired(), EqualTo('password1', 'Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_email_address(self, email_address):
        user = main.User.query.filter_by(email_address=self.email_address.data).first()
        if user:
            raise ValidationError('Email already exists. Sign in or use another email address.')


class SignInForm(FlaskForm):
    email_address = EmailField('Email Address', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Sign In')


class UpdateAccountInformationForm(FlaskForm):
    email_address = EmailField('Email Address', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    submit = SubmitField('Update Info')

    def validate_email_address(self, email_address):
        if current_user.email_address != self.email_address.data:
            user = main.User.query.filter_by(email_address=self.email_address.data).first()
            if user:
                raise ValidationError('Email already exists. Sign in or use another email address.')



