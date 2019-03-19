# models.py

from app import db
from app import admin
from flask_admin.contrib.sqla import ModelView
from flask_security import RoleMixin, UserMixin, current_user, login_required
from wtforms.fields import PasswordField

class Artist(db.Model):
	__tablename__ = 'artists'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	
	def __repr__(self):
		return "{}".format(self.name)

admin.add_view(ModelView(Artist, db.session))

class Album(db.Model):
	""""""
	__tablename__ = "albums"

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	release_date = db.Column(db.String)
	publisher = db.Column(db.String)
	media_type = db.Column(db.String)

	artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
	artist = db.relationship("Artist", backref=db.backref("albums"), order_by=id, lazy=True)

admin.add_view(ModelView(Album, db.session))

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(80), unique=True)
	description = db.Column(db.String(255))

	def __str__(self):
		return self.name

	def __hash__(self):
		return hash(self.name)


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(100))
	last_name = db.Column(db.String(100))
	login = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120))
	password = db.Column(db.String(64))
	active = db.Column(db.Boolean())
	confirmed_at = db.Column(db.DateTime())
	roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

# Customized User model for SQL-Admin
class UserAdmin(ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(ModelView):

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
		return current_user.has_role('admin')

admin.add_view(RoleAdmin(Role, db.session))	
admin.add_view(UserAdmin(User, db.session))