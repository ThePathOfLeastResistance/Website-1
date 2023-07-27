from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterUser, LoginInUser, CommentForm
from flask_gravatar import Gravatar
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from functools import wraps
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Base = declarative_base()

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


##CONFIGURE TABLES
class User(UserMixin, db.Model, Base):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key= True)
    email = db.Column(db.String(100))
    username = db.Column(db.String(50))
    password = db.Column(db.String(1000))
    children_blog = relationship("BlogPost", back_populates="parent")
    children_comment = relationship("Comment", back_populates="comment")


db.create_all()

class BlogPost(db.Model, Base):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, ForeignKey('user.id'))
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    parent = relationship("User", back_populates="children_blog")
    blog_comment = relationship("Comment", back_populates = 'commentofpost')
db.create_all()

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, ForeignKey('user.id'))
    comment = relationship("User", back_populates = 'children_comment')
    commentofpost = relationship("BlogPost", back_populates = "blog_comment")
    blog_id = db.Column(db.Integer, ForeignKey('blog_posts.id'))
db.create_all()

def Python_Decorators(func):
    @wraps(func)
    def check(post_id):
        if current_user.is_authenticated:
            if current_user == None:
                pass
            else:
                if current_user.id == 1:
                    print("this")
                    return func(post_id)
                else:
                    return abort(403)
        else:
            return abort(403)
    return check

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegisterUser()
    if request.method == "POST":
        user = db.session.query(User).filter_by(email = request.form.get('email')).first()
        if not user == None:
            flash("This Account Already Exist")
            return redirect(url_for('login'))
        else:
            NewUser = User(
                username = request.form.get('name'),
                email = request.form.get('email'),
                password = generate_password_hash(password = request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
            )
            db.session.add(NewUser)
            db.session.commit()
            login_user(NewUser)
            return redirect(url_for('get_all_posts'))
    else:
        return render_template("register.html", form = form)


@app.route('/login', methods = ['POST','GET'])
def login():
    form = LoginInUser()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email = request.form.get('email')).first()
        if not user == None:
            if check_password_hash(user.password, request.form.get('password')):
                login_user(user)
                if user.id == "1":
                    return redirect(url_for('get_all_posts'))
                else:
                    return redirect(url_for('get_all_posts'))
            else:
                flash('Wrong PassWord')
                return render_template("login.html", form = form)
        else:
            flash('User Does Not exist')
            return render_template("login.html", form = form)
    else:
        return render_template("login.html", form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods = ['POST','GET'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            newcomment = Comment(
                text = request.form.get('comment'),
                comment = current_user,
                commentofpost = requested_post
            )
            db.session.add(newcomment)
            db.session.commit()
            form = CommentForm(formdata=None)
            return render_template("post.html", post=requested_post, form=form)
        else:
            flash("Log in first before you Comment")
            return redirect(url_for('login'))
    else:
        if current_user.is_authenticated:
            if current_user.id == "1":
                return render_template("post.html", post=requested_post, form = form)
            else:
                return render_template("post.html", post=requested_post, form = form)
        else:
            return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods = ['GET', 'POST'])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            parent_id = current_user.id,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.username,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/edit-post/<int:post_id>")
@Python_Decorators
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
