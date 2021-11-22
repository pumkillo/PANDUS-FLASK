from flask import Flask, render_template, g, request, redirect, flash, url_for, make_response
from flask_login import LoginManager, login_manager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from DataBase import DataBase
from UserLogin import UserLogin
import sqlite3
import os

DATABASE = '/pandus.db'
DEBUG = True
SECRET_KEY = 'ldwq9a3adjka2kd9aufald'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'pandus.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Войдите, чтобы просматривать эту страницу'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)

dbase = None
user_login = None
rm = None

@app.before_request
def beforequest():
    global dbase
    db = get_db()
    dbase = DataBase(db)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('database.sql', mode = 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/')
def main():
    return redirect(url_for('feed'))

@app.route('/feed/')
def feed():
    postsusers = dbase.joinPostsUsers()
    return render_template('index.html', title = 'PANDUS', postsusers = postsusers)

@app.route('/create-post/', methods=['POST', 'GET'])
@login_required
def create_post():
    if request.method == "POST":
        if len(request.form['title']) > 4 and len(request.form['post_text']) > 9:
            file = request.files['image']
            if file:
                try:
                    img = file.read()
                except FileNotFoundError as err:
                    flash('Ошибка чтения файла', category='error')
            else:
                img = False
            res = dbase.addPost(request.form['title'], request.form['post_text'], current_user.get_id(), img)
            if not res:
                flash('Ошибка добавления статьи', category = 'error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash("Название статьи должно содержать не менее 5 симолов, а текст статьи - не менее 10", category='error')
            
    return render_template('create-post.html',  title="Создание поста")

@app.route('/login/', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile', id_user = current_user.get_id()))
    
    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['password'], request.form['psw']):
            global userlogin, rm
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile', id_user = current_user.getId()))

        flash('Вы ввели неверные данные', category='error')

    return render_template('login.html', title = 'Авторизация')

@app.route('/signup/', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if len(request.form['name']) > 1 and len(request.form['psw1']) > 5 and len(request.form['email']) > 10 and request.form['psw1'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw1'])
            res = dbase.addUser(request.form['name'], request.form['surname'], request.form['email'], hash)
            if res:
                flash('Вы успешно зарегистрированны',category='success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка добавление пользователя в базу данных', category='error')
        else:
            flash('Некоторые поля были заполненны некорректно', category='error')

    return render_template('signup.html', title = 'Регистрация')

@app.route('/upload/', methods = ['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash('Ошибка обновления аватара', category='error')

                flash('Аватарка обновлена', category='success')
            except FileNotFoundError as err:
                flash('Ошибка чтения файла', category='error')
        else:
            flash('Ошибка чтения файла', category='error')
    
    return redirect(url_for('settings'))

@app.route('/<id_user>/userava/')
def userava(id_user):
    id_user = dbase.getKeyId(id_user)
    img = dbase.getAvatar(id_user)
    if not img:
        with app.open_resource(app.root_path + url_for('static', filename='/img/default.png'), 'rb') as f:
            img = f.read()
    if img == 'Not Found':
        with app.open_resource(app.root_path + url_for('static', filename='/img/loading.gif'), 'rb') as f:
            img = f.read()
    h = make_response(img)
    h.headers['Content-Type'] = 'image'
    return h

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route('/post/<id_post>/')
@login_required
def post(id_post):
    postuser = dbase.getPostById(id_post)
    comments = dbase.getCommentsByIdPost(id_post)
    return render_template('post.html', title = f'Пост: {id_post}', postuser = postuser, comments = comments)

@app.route('/<id_user>/')
@login_required
def profile(id_user):
    id_user = dbase.getKeyId(id_user)
    user = dbase.getUserById(id_user)
    posts_user = dbase.getPostsOfUser(id_user)
    settings = True if current_user.get_id() == id_user else False 
    return render_template('profile.html', title = 'Profile', user = user, posts_user = posts_user, settings = settings)

@app.route('/settings/')
@login_required
def settings():
    return render_template('settings.html', title = 'Настройки профиля')

@app.route('/<id_post>/comment/', methods = ['GET', 'POST'])
@login_required
def comment(id_post):
    if request.method == 'POST':
        if request.form['comment'].strip() != '':
            res = dbase.addComment(current_user.get_id(), id_post, request.form['comment'].strip())
            if not res:
                flash('Ошибка добавления комментария', category='error')
        else:
            flash('Помимо пробелов Ваш комментарий должен содержать другие символы', category='error')
    return redirect(url_for('post', id_post = id_post))

@app.route('/edit-inf/', methods = ['GET', 'POST'])
@login_required
def editinf():
    if request.method == 'POST':    
        if current_user.getId() != request.form['id'] or current_user.getName() != request.form['name'] or current_user.getSurname() != request.form['surname'] or current_user.getAbout() != request.form['about']:
            if dbase.checkId(request.form['id']) and current_user.getId() != request.form['id']:
                flash('Такой id уже существует', category='error')
            res = dbase.editUserInfo(request.form['id'], request.form['name'], request.form['surname'], request.form['about'], current_user.getEmail())
            if res:
                flash('Данные успешно обновлены', category='success')
            else:
                flash('Произошла ошибка при изменении данных', category='error')
        else:
            flash('Вы не изменили информацию профиля', category='success')

    return redirect(url_for('settings'))   

@app.route('/delete-user/')
@login_required
def deleteUser():
    res = dbase.deleteUser(current_user.get_id())
    if res:
        return redirect(url_for('logout'))
    flash('Ошибка при удалении пользователя', category='error')

@app.route('/<id_post>/<id_comment>/delete-com/')
@login_required
def deleteCom(id_comment, id_post):
    res = dbase.deleteCom(id_comment)
    if res:
            return redirect(url_for('post', id_post = id_post))
    flash('Ошибка при удалении комментария пользователя', category='error')

@app.route('/<id_post>/<id_comment>/edit-comm/', methods=['GET', 'POST'])
@login_required
def edit_comm(id_comment, id_post):
    if request.method == 'POST':
        if request.form['text'].strip() != '':
            res = dbase.editComment(id_comment, request.form['text'])
            if not res:
                flash('Произошла ошибка при редактировании комментария', category='error')
        else:
            flash('Помимо пробелов Ваш комментарий должен содержать другие символы', category='error')

    return redirect(url_for('post', id_post = id_post))   

@app.route('/<id_post>/image/')
def image(id_post):
    img = dbase.getPostById(id_post)['img']
    if not img:
        return False
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


create_db()
app.run(debug=True)