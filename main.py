from flask import Flask, render_template, redirect, url_for, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, login_required,UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
import forms
import os


app = Flask(__name__)



class MyAnonymousUserMixin(ModelView):
    is_admin = True


login_manager = LoginManager(app)

login_manager.login_view = 'sign_in'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'


admin = Admin(app)

bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '(/("ZOHDAJK)()kafau029)ÖÄ:ÄÖ:"OI§)"Z$()&"()!§(=")/$'
app.config['STATIC_FOLDER'] = 'static'

db = SQLAlchemy(app)


user_group = db.Table('user_group',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('group_id', db.Integer, db.ForeignKey('groups.id')))


class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    following = db.relationship('Groups', secondary=user_group, backref='followers')

    def __str__(self):
        return f'<User: {self.first_name}>'


class Groups(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    userid = db.Column(db.Integer, nullable=False)
    notes = db.relationship("Notes")

    def __str__(self):
        return self.name


class Notes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150), nullable=False)
    text = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    group = db.relationship('Groups', back_populates='notes')
    image = db.Column(db.String(150))

    def __str__(self):
        return self.description


db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.email_address == "ernis@gmail.com"


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Groups, db.session))
admin.add_view(MyModelView(Notes, db.session))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    form = forms.AddCategory()
    if form.validate_on_submit():
        column = Groups(

            name=form.name.data,
            description=form.description.data,
            userid=current_user.id
        )

        db.session.add(column)
        db.session.commit()
        current_user.following.append(column)
        db.session.commit()

        return render_template('success.html')
    return render_template('add_category.html', form=form)


@login_required
@app.route('/edit_category', methods=['GET', 'POST'])
def edit_cat():
    form = forms.EditCat()
    search = request.args.get("id")
    if request.method == 'GET':
        group = Groups.query.filter_by(id=search).first()
        form.name.data = group.name
        form.description.data = group.description
    if form.validate_on_submit():
        group = Groups.query.filter_by(id=search).first()
        group.name = form.name.data
        group.description = form.description.data
        db.session.commit()
        flash('Category information updated', 'success')
        return render_template('success.html')
    return render_template('edit_cat.html', form=form)


@login_required
@app.route('/add_note', methods=['GET', 'POST'])
def add_note():
    form = forms.AddNote()
    if form.validate_on_submit() and request.method == 'POST':
        image_data = form.image.data
        if image_data:
            file_name = image_data.filename
            file_extension = os.path.splitext(file_name)[1]
            file_name += file_extension
            image_data.save(os.path.join(app.config['STATIC_FOLDER'], file_name))
            file_path = os.path.join('static', file_name)
            column = Notes(
                image=file_path,
                description=form.description.data,
                text=form.text.data,
                group_id=form.groups.data.id
             )
            db.session.add(column)
            db.session.commit()
            return render_template('success.html')
        else:
            column = Notes(
                description=form.description.data,
                text=form.text.data,
                group_id=form.groups.data.id
            )
            db.session.add(column)
            db.session.commit()
            return render_template('success.html')

    return render_template('Add_Note.html', form=form)


@app.route('/show')
@login_required
def show():
    a = []
    for x in current_user.following:
        a.append(
            {'id': x.id, 'name': x.name, 'description': x.description})

    return render_template('categories.html', data=a)



@app.route('/my_notes')
@login_required
def my_notes():
    category = request.args.get('category')
    i = User.query.filter_by(email_address=current_user.email_address).first()
    following_groups = i.following
    notes = []
    categories =[]
    for cat in following_groups:
        categories.append(cat.name)
    for group in following_groups:
        if category is None or group.name == category:
            group_notes = group.notes
            notes.extend(group_notes)
    return render_template('MyNotes.html', notes=notes, categories=categories)


@login_required
@app.route('/delete_cat', methods=['GET', 'POST'])
def delete_cat():
    search = request.args.get("id")
    # data = Groups.query.filter_by(userid=current_user.id)
    # data = current_user.following.all()
    Groups.query.filter_by(id=search)
    group_id = search
    Groups.query.filter_by(id=group_id).delete()
    db.session.commit()

    return render_template('success.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode()
        user = User(
            first_name=form.first_name.data,
            email_address=form.email_address.data,
            last_name=form.last_name.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {current_user.first_name}', 'success')
        return redirect(url_for('show'))
    return render_template('register.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            # flash(f'Welcome, {current_user.first_name}', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash(f'User or password does not match', 'danger')
        return render_template('categories.html', form=form)
    return render_template('sign_in.html', form=form)


@app.route('/update_account_information', methods=['GET', 'POST'])
@login_required
def update_account_information():
    form = forms.UpdateAccountInformationForm()
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email_address.data = current_user.email_address
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email_address = form.email_address.data
        db.session.add(user)
        db.session.commit()
        flash('User information updated', 'success')
        return redirect(url_for('update_account_information'))
    return render_template('update_account_information.html', form=form)


@login_required
@app.route('/sign_out')
def sign_out():
    logout_user()
    flash('Goodbye, see you next time', 'success')
    return render_template('home.html')


@app.route('/delete_note/<note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Notes.query.get(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('my_notes'))

@app.route('/edit_note/<note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Notes.query.get(note_id)
    i = User.query.filter_by(email_address=current_user.email_address).first()
    categories = Groups.query.filter_by(userid=current_user.id).all()

    if request.method == 'POST':
        note.description = request.form['description']
        note.text = request.form['text']
        note.group_id = request.form['category']
        db.session.commit()
        return redirect(url_for('my_notes'))
    return render_template('edit_note.html', note=note, categories=categories)


@app.route('/search_my_notes', methods=['POST'])
@login_required
def search_my_notes():
    search_term = request.form['search_term']
    notes = (
        db.session.query(Notes)
        .join(Groups)
        .filter(Notes.description.contains(search_term), Groups.userid == current_user.id)
        .all()
    )
    return render_template('MyNotes.html', notes=notes)


if __name__ == '__main__':
    app.run(debug=True)
