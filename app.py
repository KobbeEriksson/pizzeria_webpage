from flask import Flask, render_template, redirect, url_for, request, session, flash
import pandas as pd

from models import db, User

file = "../flaskpizza/pizzeria.csv"
pizzas = pd.read_csv(file)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {str(e)}")


@app.cli.command('initdb')
def initdb_command():
    db.create_all()
    print('Database initialized')


@app.route('/')
def home():
    return render_template('home.html', pizzas=pizzas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user not in session:
            # set a session variable to indicate that the user is logged in
            session['user_id'] = user.id
            print(session)
            print(session['user_id'])
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        num_users = User.query.count()
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('signup.html', error=True)
        elif password != confirm_password:
            return render_template('signup.html', error=True)
        elif num_users == 0:
            new_user = User(email=email,
                            username=username,
                            password=password,
                            is_admin=True)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('home'))
        else:
            new_user = User(email=email,
                            username=username,
                            password=password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('home'))
    return render_template('signup.html')


@app.route('/profile')
def profile():
    # check if user_id is in session
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    # get user information from database using user_id
    user = User.query.filter_by(id=session['user_id']).first()

    return render_template('profile.html', username=user.username)


@app.route('/admin')
def admin():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    user = User.query.filter_by(id=session['user_id']).first()
    if not user.is_admin:
        flash('You are not authorized to access this page.')
        return redirect(url_for('home'))
    else:
        return render_template('admin.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_username', None)
    return redirect(url_for('home'))


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(request.form['Name'])
    session.modified = True  # mark the session as modified to make sure the changes are saved

    # update the number of items in the cart
    session['cart_count'] = session.get('cart_count', 0) + int(request.form['quantity'])

    # redirect to the same page with the hashtag
    return redirect(url_for('home', _anchor='menu'))


@app.route('/remove_from_cart/<item>')
def remove_from_cart(item):
    session['cart'].remove(item)
    return redirect(url_for('home', _anchor='menu'))



@app.route('/empty_cart')
def empty_cart():
    session.pop('cart', None)
    return redirect(url_for('home', _anchor='menu'))


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('home', _anchor='menu'))
    else:
        return redirect(url_for('home', _anchor='menu'))


if __name__ == '__main__':
    app.run(debug=True)
