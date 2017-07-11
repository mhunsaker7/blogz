from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:abc123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def  __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['signup', 'login', 'index', 'blog_posts']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/signup')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog') 

@app.route('/blog', methods=['GET']) 
def blog_posts():
    print(request.args)

    if request.args.get('id') != None:
        new_id = request.args.get('id')
        blog_post = db.session.query(Blog).filter_by(id=new_id).first()
        body = blog_post.body
        title = blog_post.title
        owner = blog_post.owner.username
        new_owner = db.session.query(User).filter_by(username=owner).first()
        owner_id = new_owner.id
        return render_template('blogpost.html', title=title, body=body, owner=owner, owner_id=owner_id)
    if request.args.get('user') != None:
        new_user = request.args.get('user')
        user = db.session.query(User).filter_by(id=new_user).first()
        posts = db.session.query(Blog).filter_by(owner_id=new_user).all()
        return render_template('blogbyuser.html', blogs=posts, user=user)
    else:
        return render_template('blog.html', blogs = get_blog_posts())

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup(): 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if (username == "") or (" " in username) or (len(username) <= 3):
            flash("That's not a valid username", 'error') 
            username = "" 

        elif (password == "") or (" " in password) or (len(password) <= 3):
            flash("That's not a valid password", 'error') 

        elif verify != password:
            flash("Passwords to not match", 'error') 

        elif existing_user:
            flash('Username Already Exists', 'error') 

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
            
    return render_template('signup.html')  


def get_blog_posts():
    return Blog.query.all()

@app.route('/')  
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == '':
            flash('Please enter a title for your new blog post', 'error')
            return render_template('newpost.html', body=body)
        if body == '':
            flash('Please enter a body for your new blog post', 'error')
            return render_template('newpost.html', title=title)
        blog = Blog(title=title, body=body, owner=owner)
        db.session.add(blog)
        db.session.commit()
        return redirect('/blog?id=' + str(blog.id))
    
    return render_template('newpost.html')




app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()