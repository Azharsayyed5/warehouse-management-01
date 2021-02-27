from flask import Flask
from flask import Flask,request,redirect,render_template, send_from_directory, send_file, redirect, url_for, request, flash
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, current_user, login_user, logout_user, login_required, LoginManager
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import aliased
from flask_paginate import Pagination, get_page_parameter
import datetime
import uuid
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder="../frontend/", static_folder='reports')

# Set up the SQLAlchemy Database to be a local file 'desserts.database'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
app.config['SECRET_KEY'] = 'randomKey'

# Initialize templates
app.config['HomeTemplate'] = "Home.html"
app.config['ViewProductsTemplate'] = "ViewProducts.html"
app.config['UpdateProductTemplate'] = "UpdateProduct.html"
app.config['DeleteProductTemplate'] = "DeleteProduct.html"
app.config['ViewLocationsTemplate'] = "ViewLocations.html"
app.config['UpdateLocationTemplate'] = "UpdateLocation.html"
app.config['DeleteLocationTemplate'] = "DeleteLocation.html"
app.config['ViewMovementsTemplate'] = "ViewMovements.html"
app.config['ViewReportTemplate'] = "ViewReport.html"
app.config['UpdateMovementTemplate'] = "UpdateMovement.html"
app.config['DeleteMovementTemplate'] = "DeleteMovement.html"
app.config['LoginTemplate'] = "login.html"
app.config['SignupTemplate'] = "signup.html"

# Set SQLALCHEMY_TRACK_MODIFICATIONS to False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

ROWS_PER_PAGE = 5

class ProductView(MethodView):

    @login_required
    def get(self):

        page = request.args.get(get_page_parameter(), type=int, default=1)
        product_list = Product.query.paginate(page=page, per_page=ROWS_PER_PAGE)
        return render_template(
            app.config['ViewProductsTemplate'], products=product_list
            )

    @login_required
    def post(self):
        try:
            product_detail = request.form["product-name"]
            new_product = Product(name=product_detail)
            database.session.add(new_product)
            database.session.commit()
        except:
            pass
        finally:
            return redirect('/products')

class ProductUpdateView(MethodView):
    
    @login_required
    def get(self, id=None,  method=None):
        product_detail = Product.query.get_or_404(id)
        if method == 'update':
            return render_template(app.config['UpdateProductTemplate'], product=product_detail)
        elif method == 'delete':
            return render_template(app.config['DeleteProductTemplate'] , product=product_detail)
        else:
            return 'Wrong method'

    @login_required
    def post(self, id=None, method=None):
        try:
            product = Product.query.get_or_404(id)
            if method == 'update':
                product.name = request.form['product-name']
                database.session.commit()   
            elif method == 'delete':
                product.id = id
                if product:
                    database.session.delete(product)
                    database.session.commit() 
            else:
                return 'Wrong method'
        except:
            pass
        finally:
            return redirect('/products')

class LocationsView(MethodView):

    @login_required
    def get(self):
        page = request.args.get(get_page_parameter(), type=int, default=1)
        location_list = Location.query.paginate(page=page, per_page=ROWS_PER_PAGE)
        return render_template(app.config['ViewLocationsTemplate'], locations=location_list)

    @login_required
    def post(self):
        try:
            location = request.form["location-name"]
            new_location = Location(name=location)
            database.session.add(new_location)
            database.session.commit()  
        except:
            pass
        finally:
            return redirect('/locations')

class LocationUpdateView(MethodView):

    @login_required
    def get(self, id=None, method=None):
        location_detail = Location.query.get_or_404(id)
        if method == 'update':
            return render_template(app.config['UpdateLocationTemplate'], location=location_detail)
        elif method == 'delete':
            return render_template(app.config['DeleteLocationTemplate'], location=location_detail)
        else:
            return 'Wrong method'
        
    @login_required
    def post(self, id=None, method=None):
        try:
            location = Location.query.get_or_404(id)
            if method == 'update':
                if location:
                    location.name = request.form['location-name']
                    database.session.commit()
            elif method == 'delete':
                location.id = id
                if location:
                    database.session.delete(location)
                    database.session.commit()
            else:
                return 'Wrong method'
        except:
            pass
        finally:
            return redirect('/locations')

class MovementView(MethodView):
    
    @login_required
    def get(self):

        """
            SELECT p.name as product_name, l2.name as source_location, l.name as destination_location,  m.quantity
            FROM movement m
            LEFT JOIN product p ON m.product_id = p.id
            LEFT JOIN location l ON m.destination_location_id  = l.id 
            LEFT JOIN location l2 ON m.source_location_id  = l2.id OR (m.source_location_id IS NULL)
            ORDER BY m.timestamp desc;
        """
        products = Product.query.all()
        locations = Location.query.all()

        Location1 = aliased(Location)
        Location2 = aliased(Location)

        page = request.args.get(get_page_parameter(), type=int, default=1)
        data = Movement.query.join(
            Product, Movement.product_id == Product.id, isouter=True).join(
                Location1, Movement.destination_location_id  == Location1.id, isouter=True).join(
                Location2, Movement.source_location_id  == Location2.id, isouter=True).add_columns(
                        Movement.movement_id.label('movement_id'),
                        Product.name.label('product'), 
                        Location2.name.label('source_location'),  
                        Location1.name.label('destination_location'), 
                        Movement.quantity.label('quantity')
                        ).paginate(page=page, per_page=ROWS_PER_PAGE)
        print(data)
        return render_template(
                app.config['ViewMovementsTemplate'], 
                data=data,
                products=products,
                locations=locations
            )

    @login_required
    def post(self):
        try:
            destination_location = request.form['destination-location']
            source_location = request.form['source-location']
            product = request.form['product']
            quantity = request.form['quantity']
            add_movement = Movement(
                destination_location_id=destination_location, source_location_id=source_location, 
                product_id=product, quantity=quantity
                )
            database.session.add(add_movement)
            database.session.commit()
        except:
            pass
        finally:
            return redirect('/movements')

class MovementUpdateView(MethodView):
    
    @login_required
    def get(self, movement_id=None, method=None):
        if method == 'update':
            product_list, locations_list, movements_list = Product.query.all(), Location.query.all(),  Movement.query.all()
            return render_template(
                    app.config['UpdateMovementTemplate'], 
                    products=product_list,
                    locations=locations_list,
                    movements=movements_list
                )
        elif method == 'delete':
            movement = Movement.query.get_or_404(movement_id)
            return render_template(app.config['DeleteMovementTemplate'], movement=movement)
        else:
            return "wrong method"

    @login_required
    def post(self, movement_id=None, method=None):
        try:
            if method == 'update':
                Movement = Movement.query.get_or_404(movement_id)
                if Movement:
                    Movement.destination_location = request.form['destination-location']
                    Movement.source_location = request.form['source-location']
                    Movement.product = request.form['product']
                    Movement.quantity = request.form['quantity']
                    database.session.commit()
            elif method == 'delete':
                movement = Movement.query.get_or_404(movement_id)
                movement.movement_id = movement_id
                if movement:
                    database.session.delete(movement)
                    database.session.commit()
            else:
                return "wrong method"
        except:
            pass
        finally:
            return redirect('/movements')

last_csv_created_at = None

class ReportView(MethodView):

    @login_required
    def get(self):

        """
            SELECT p.name as product, l.name as location, sum(m.quantity) as quantity
            FROM movement m
            INNER JOIN product p ON m.product_id = p.id
            INNER JOIN location l ON m.destination_location_id  = l.id 
            GROUP BY m.product_id, m.destination_location_id
            ORDER BY m.timestamp desc;
        """

        page = request.args.get(get_page_parameter(), type=int, default=1)
        sort = request.args.get('sort', 'asc')
        field = request.args.get('field', 'timestamp')

        if sort == 'asc':
            order = getattr(Movement, field).asc()
        else:
            order = getattr(Movement, field).desc()

        reports = Movement.query.join(
            Product, Movement.product_id == Product.id).join(
                Location, Movement.destination_location_id  == Location.id).group_by(
                    Movement.product_id, Movement.destination_location_id).add_columns(
                        Product.name.label('product'),
                        Location.name.label('location'),
                        func.sum(Movement.quantity).label('quantity')
                        ).order_by(order).paginate(page=page, per_page=ROWS_PER_PAGE)
        # try:
        #     global last_csv_created_at
        #     current_minute = datetime.datetime.now().minute
        #     if current_minute != last_csv_created_at:
        #         last_csv_created_at = current_minute
        #         print(f"CSV Created at {datetime.datetime.now()}")
        #         df =pd.DataFrame(reports)
        #         df.to_csv("reports/latest_report.csv", index=False)
        # except:
        #     pass

        return render_template(app.config['ViewReportTemplate'], report=reports)

class HomeView(MethodView):
    
    @login_required
    def get(self):
        return render_template(app.config['HomeTemplate'])

@app.route('/download_report/<string:filename>')
@login_required
def download_report(filename):
    try:
        reports = Movement.query.join(
            Product, Movement.product_id == Product.id).join(
                Location, Movement.destination_location_id  == Location.id).group_by(
                    Movement.product_id, Movement.destination_location_id).add_columns(
                        Product.name.label('product'),
                        Location.name.label('location'),
                        func.sum(Movement.quantity).label('quantity')
                        ).all()
        try:
            df =pd.DataFrame(reports)
            df.to_csv("reports/latest_report.csv", index=False)
        except:
            pass
        DOWNLOAD_DIRECTORY = 'reports'
        return send_file("reports/latest_report.csv", as_attachment=True)
    except:
        "Not Found"

@app.route('/login')
def login():
    return render_template(app.config['LoginTemplate'])

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))
    login_user(user, remember=remember)
    return redirect(url_for('home'))

@app.route('/signup')
def signup():
    return render_template(app.config['SignupTemplate'])

@app.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if user: 
        flash('Email address already exists')
        return redirect(url_for('signup'))
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    database.session.add(new_user)
    database.session.commit()
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

def generate_uuid():
    return str(uuid.uuid4())

# START : Database ORM initialization

class Product(database.Model):
    __tablename__ = 'product'
    id = database.Column(database.String(255), primary_key=True, default=generate_uuid)
    name = database.Column(database.String(255), nullable=False)

    def __repr__(self):
        return '<Product %r>' % self.id

class Location(database.Model):
    __tablename__ = 'location'
    id = database.Column(database.String(255), primary_key=True, default=generate_uuid)
    name= database.Column(database.String(255))

    def __repr__(self):
        return '<Location %r>' % self.id

class Movement(database.Model):
    movement_id= database.Column(database.String(255), primary_key=True, default=generate_uuid)
    timestamp = database.Column(database.DateTime(timezone=True), default=func.now())
    product_id= database.Column(database.String(255), database.ForeignKey('product.id'))
    product = database.relationship("Product")
    destination_location_id = database.Column(database.String(255), database.ForeignKey('location.id'))
    destination_location = database.relationship("Location", primaryjoin=destination_location_id==Location.id)
    source_location_id = database.Column(database.String(255),database.ForeignKey('location.id'))
    source_location = database.relationship("Location", primaryjoin=source_location_id==Location.id)
    quantity = database.Column(database.String(255))

    def __repr__(self):
        return '<Movement %r>' % self.movement_id

class User(UserMixin, database.Model):
    id = database.Column(database.String(255), primary_key=True, default=generate_uuid)
    email = database.Column(database.String(100), unique=True)
    password = database.Column(database.String(100))
    name = database.Column(database.String(1000))

    def __repr__(self):
        return '<id %r>' % self.id

# END : Database ORM initialization

database.create_all()
app.add_url_rule('/products',view_func=ProductView.as_view('/products'))
app.add_url_rule('/locations',view_func=LocationsView.as_view('/locations'))
app.add_url_rule('/movements',view_func=MovementView.as_view('movements'))
app.add_url_rule('/report',view_func=ReportView.as_view('report'))
app.add_url_rule('/home',view_func=HomeView.as_view('home'))
app.add_url_rule('/products/<string:id>/<string:method>',view_func=ProductUpdateView.as_view('productsUpdate'))
app.add_url_rule('/locations/<string:id>/<string:method>',view_func=LocationUpdateView.as_view('locationUpdate'))
app.add_url_rule('/movements/<string:movement_id>/<string:method>',view_func=MovementUpdateView.as_view('/MovementsUpdate'))



