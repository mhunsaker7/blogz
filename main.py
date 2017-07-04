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
    allowed_routes = ['signup', 'login']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/signup')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog') 

@app.route('/blog', methods=['GET']) 
def blog_posts():
    print(request.args)

    if request.args.get('id') == None:
        return render_template('blog.html', blogs = get_blog_posts())
    else:
        new_id = request.args.get('id')
        blog_post = db.session.query(Blog).filter_by(id=new_id).first()
        body = blog_post.body
        title = blog_post.title
        return render_template('blogpost.html', title=title, body=body)


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

        # validate username and password and verify

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username Already Exists', 'error') 
            
    return render_template('signup.html')  


def get_blog_posts():
    return Blog.query.all()

@app.route('/')  
def home():
    return render_template('blog.html', blogs = get_blog_posts())

@app.route('/newpost', methods=['POST', 'GET'])
def index():
    
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