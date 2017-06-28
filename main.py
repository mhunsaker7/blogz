from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hunsam3l@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(200))

    def  __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['GET']) 
def blog_posts():
    return render_template('blog.html', blogs = get_blog_posts())

def get_blog_posts():
    return Blog.query.all()

@app.route('/newpost', methods=['POST', 'GET'])
def index():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == '':
            flash('Please enter a title for your new blog post', 'error')
            return render_template('newpost.html', body=body)
        if body == '':
            flash('Please enter a body for your new blog post', 'error')
            return render_template('newpost.html', title=title)
        blog = Blog(title=title, body=body)
        db.session.add(blog)
        db.session.commit()
        return redirect("/blog")
    
    return render_template('newpost.html')

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()