from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db_users = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tittle = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.tittle


class User(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.tittle


uAdmin = User(name='admin', address='', phone='', password='admin', isAdmin=True)

admin = False
login = False


@app.before_first_request
def create_tables():
    db.create_all()
    db_users.create_all()


@app.route('/')  # '/' - главная страница
def index():
    global login
    items = Item.query.order_by(Item.price).all()

    if login == True:
        return render_template('index_authorized.html', data=items)
    else:
        return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        password = request.form['password']

        user = User(name=name, address=address, phone=phone, password=password)

        try:
            db_users.session.add(user)
            db_users.session.commit()
            return redirect('/')
        except:
            return "Ошибка регистрации пользователя"
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    global login, admin
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']

        try:
            if name == 'admin' and password == 'admin':
                admin = True
            else:
                admin = False

            login = True
            return redirect('/')
        except:
            return "Ошибка авторизации"
    else:
        return render_template('login.html')


@app.route('/buy/<int:id>')
def item_buy(id):
    global login

    if login == True:
        item = Item.query.get(id)

        api = Api(merchant_id=1396424,
                  secret_key='test')
        checkout = Checkout(api=api)  # страничка оплаты
        data = {
            "currency": "BYN",
            "amount": str(item.price) + "00"
        }
        url = checkout.url(data).get('checkout_url')
        return redirect(url)
    else:
        return login()


@app.route('/create', methods=['POST', 'GET'])
def create():
    global login, admin
    if login == True and admin == True:
        if request.method == "POST":
            tittle = request.form['tittle']
            price = request.form['price']
            text = request.form['text']

            item = Item(tittle=tittle, price=price, text=text)

            try:
                db.session.add(item)
                db.session.commit()
                return redirect('/')
            except:
                return "Ошибка создания товара"
        else:
            return render_template('create.html')
    else:
        return "У вас нет прав"


if __name__ == "__main__":
    app.run(debug=True)  # чтобы видеть ошибки на сайте
