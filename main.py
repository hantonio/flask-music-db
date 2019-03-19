# test.py

from app import app
from app import db
from db_setup import init_db, db_session
from forms import MusicSearchForm, AlbumForm
from flask import flash, render_template, request, redirect
from models import Album, Artist, User, Role
from tables import Results
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, utils, login_required

init_db()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Executes before the first request is processed.
@app.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='end-user', description='End user')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = utils.encrypt_password('password')
    if not user_datastore.get_user('someone@example.com'):
        user_datastore.create_user(email='someone@example.com', password=encrypted_password)
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(email='admin@example.com', password=encrypted_password)

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user('someone@example.com', 'end-user')
    user_datastore.add_role_to_user('admin@example.com', 'admin')
    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('index.html', form=search)


@app.route('/results')
def search_results(search):
    results=[]
    search_string = search.data['search']

    if search_string:
        if search.data['select'] == 'Artist':
            qry = db_session.query(Album, Artist).filter(
                Artist.id==Album.artist_id).filter(
                    Artist.name.contains(search_string))
            results = [item[0] for item in qry.all()]
        elif search.data['select'] == 'Album':
            qry = db_session.query(Album).filter(
                Album.title.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Publisher':
            qry = db_session.query(Album).filter(
                Album.publisher.contains(search_string))
            results = qry.all()
        else:
            qry = db_session.query(Album)
            results = qry.all()
    else:
        qry = db_session.query(Album)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)


@app.route('/item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    qry = db_session.query(Album).filter(Album.id==id)
    album = qry.first()

    if album:
        form = AlbumForm(formdata=request.form, obj=album)
        if request.method == 'POST' and form.validate():
            # save edits
            save_changes(album, form)
            flash('Album updated successfully!')
            return redirect('/')
        return render_template('edit_album.html', form=form)
    else:
        return 'Error loading #{id}'.format(id=id)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete the item in the database that matches the specified
    id in the URL
    """
    qry = db_session.query(Album).filter(Album.id==id)
    album = qry.first()

    if album:
        form = AlbumForm(formdata=request.form, obj=album)
        if request.method == 'POST' and form.validate():
            # delete the item from the database
            db_session.delete(album)
            db_session.commit()

            flash('Album deleted successfully!')
            return redirect('/')
        return render_template('delete_album.html', form=form)
    else:
        return 'Error deleting #{id}'.format(id=id)


@app.route('/new_album', methods=['GET', 'POST'])
@login_required
def new_album():
    """ Add a new album """
    form = AlbumForm(request.form)

    if request.method == 'POST' and form.validate():
        # save the album
        album = Album()
        save_changes(album, form, new=True)
        flash('Album created successfully!')
        return redirect('/')

    return render_template('new_album.html', form=form)


def save_changes(album, form, new=False):
    """ Save the changes to the database """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object
    artist = Artist()
    artist.name = form.artist.data

    album.artist = artist
    album.title = form.title.data
    album.release_date = form.release_date.data
    album.publisher = form.publisher.data
    album.media_type = form.media_type.data

    if new:
        # Add the new album to the database
        db_session.add(album)

    db_session.commit();


if __name__ == '__main__':
    app.run()
