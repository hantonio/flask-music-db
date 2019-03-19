# forms.py

from wtforms import Form, StringField, SelectField, PasswordField, BooleanField, validators
from wtforms.fields.html5 import EmailField
from flask_security import LoginForm

class MusicSearchForm(Form):
	choices = [('Artist', 'Artist'),
				('Album', 'Album'),
				('Publisher', 'Publisher')]
	select = SelectField('Search for music:', choices=choices)
	search = StringField('')

class AlbumForm(Form):
	media_types = [('Digital', 'Digital'),
					('CD', 'CD'),
					('Cassete Tape', 'Cassete Tape')
					]
	artist = StringField('Artist')
	title = StringField('Title')
	release_date = StringField('Release Date')
	publisher = StringField('Publisher')
	media_type = SelectField('Media', choices=media_types)

class ExtendedLoginForm(LoginForm):
    email = EmailField('Email', [validators.DataRequired(message='email is required '), validators.Email(message='invalid email address')])
    password = PasswordField('Password', [validators.DataRequired(message='password is required')])
    remember = BooleanField('Remember Me')