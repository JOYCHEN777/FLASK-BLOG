from flask import render_template, url_for, request, redirect, flash
from blog import app, db
from blog.models import User, Post, Comment, Rate
from blog.forms import RegistrationForm, LoginForm, CommentForm, EditProfileForm, PostForm, SearchForm, RateForm, \
    SortForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from sqlalchemy import or_, func


@app.route("/")
@app.route("/home")
def home():
    user=User.query.filter_by(username='joychen').first()
    posts = Post.query.filter_by(user=user).all()
    new_posts = Post.query.order_by(Post.date.desc()).limit(5)
    return render_template('home.html', title='Home', posts=posts, new_posts=new_posts)


@app.route("/all_posts/", methods=['GET', 'POST'])
def all_posts():
    posts = Post.query.order_by(Post.date.desc()).all()
    form = SortForm()
    sort_way = form.sort.data
    if form.validate_on_submit():
        if sort_way == 1:
            posts = Post.query.order_by('date').all()
    return render_template('all_posts.html', title='All Posts', posts=posts, form=form)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/success")
def success():
    return render_template('success.html', title='successful registered')


@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter(Comment.post_id == post.id)
    c_form = CommentForm()
    r_form = RateForm()
    rate = Rate.query.filter_by(author_id=current_user.id, post_id=post_id).first()
    state = False
    if rate:
        state = True
    return render_template('post.html', post=post, comments=comments, c_form=c_form, r_form=r_form, state=state)


@app.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])
@login_required
def post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    c_form = CommentForm()
    r_form = RateForm()
    rate = Rate.query.filter_by(author_id=current_user.id, post_id=post_id).first()
    state = False
    if rate:
        state = True
    if c_form.validate_on_submit():
        db.session.add(Comment(content=c_form.comment.data, post_id=post.id, author_id=current_user.id))
        db.session.commit()
        flash("Your comment has been added to the post", "success")
        return redirect(f'/post/{post.id}')
    comments = Comment.query.filter(Comment.post_id == post.id)
    return render_template('post.html', post=post, comments=comments, c_form=c_form, r_form=r_form, state=state)


@app.route('/post/<int:post_id>/rate', methods=['GET', 'POST'])
@login_required
def rate(post_id):
    post = Post.query.get_or_404(post_id)
    c_form = CommentForm()
    r_form = RateForm()
    rate = Rate.query.filter_by(author_id=current_user.id, post_id=post_id).first()
    state = False
    if rate:
        state = True
    elif r_form.validate_on_submit():
        db.session.add(Rate(rate=int(r_form.rate.data), post_id=post.id, author_id=current_user.id))
        db.session.commit()
        # rate_sum =db.session.query(func.sum(Rate.rate)).filter(Rate.post_id == post_id).
        rate_sum = Rate.query.filter(Rate.post_id == post_id).with_entities(func.sum(Rate.rate)).scalar()
        rate_num = Rate.query.filter(Rate.post_id == post_id).count()
        average_rate = format(rate_sum / rate_num, '.1f')
        post.average_rate = average_rate
        post.rate_num = rate_num
        db.session.commit()
        flash("successful rated", "success")
        return redirect(f'/post/{post.id}')
    comments = Comment.query.filter(Comment.post_id == post.id)
    return render_template('post.html', post=post, comments=comments, r_form=r_form, c_form=c_form, state=state)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        login_user(user)
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid email address or password.')
            flash('Please try again!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            flash('Login successful!')
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user=user).all()
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    posts = Post.query.filter_by(user=current_user).all()
    if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).all():
        flash('username already exist, please choose another one!')
        return render_template('edit_profile.html', title='Edit Profile',
                               form=form)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        # 这里要改，post要加一下
        return render_template('user.html', user=current_user, posts=posts)
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/post_blog', methods=['GET', 'POST'])
@login_required
def post_blog():
    form = PostForm()
    if form.validate_on_submit():
        db.session.add(Post(content=form.content.data, title=form.title.data, author_id=current_user.id))
        db.session.commit()
        flash('Posted!')
        return redirect(url_for('home'))
    return render_template("post_blog.html", title='Post Blog', form=form)


@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search_info = form.info.data
        like_s = "%{}%".format(str(search_info))
        if form.type.data == 1:
            search_results = Post.query.filter(Post.title.like(like_s)).all()
        elif form.type.data == 2:
            search_results = Post.query.filter(Post.content.like(like_s)).all()
        else:
            search_results = Post.query.filter(or_(Post.content.like(like_s),
                                                   Post.title.like(like_s))).all()
        # if search_results is not None:
        return render_template('search_result.html', title='Result', posts=search_results, info=search_info, form=form)
    return render_template('search.html', title='Search', form=form)


@app.route("/test")
def test1():
    post = {
        'user': {'username': 'john2'},
        'content': 'content_test2',
        'image_file': 'default.jpg',
        'title': 'title_test2',
        'date': '2021-02-18',
        'id': '2'
    }
    comments = [
        {
            'user': {'username': 'john'},
            'content': 'comment_test1',
            'title': 'title_test1',
            'date': '2021-02-18',
            'id': '1'
        }]
    form = CommentForm()
    return render_template('post.html', post=post, comments=comments, c_form=form)
