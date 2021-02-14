from flask import Flask
from flask import Flask,request,redirect,render_template
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from datetime import datetime
import uuid

app = Flask(__name__, template_folder="../frontend/")

# Set up the SQLAlchemy Database to be a local file 'desserts.database'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'

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

# Set SQLALCHEMY_TRACK_MODIFICATIONS to False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template(app.config['HomeTemplate'])

class ProductView(MethodView):

    def get(self):
        product_list = Product.query.all()
        return render_template(app.config['ViewProductsTemplate'], products=product_list)

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

    def get(self, id=None):
        product_detail = Product.query.get_or_404(id)
        return render_template(app.config['UpdateProductTemplate'], product=product_detail)

    def post(self, id=None):
        try:
            product = Product.query.get_or_404(id)
            product.name = request.form['product-name']
            database.session.commit()   
        except:
            pass
        finally:
            return redirect('/products')


class ProductDestroyView(MethodView):

    def get(self, id=None):
        product = Product.query.get_or_404(id)
        return render_template(app.config['DeleteProductTemplate'] , product=product)

    def post(self, id=None):
        try:
            product = Product.query.get_or_404(id)
            product.id = id
            if product:
                database.session.delete(product)
                database.session.commit()   
        except:
            pass
        finally:
            return redirect('/products')

class LocationsView(MethodView):

    def get(self):
        location_list = Location.query.all()
        return render_template(app.config['ViewLocationsTemplate'], locations=location_list)

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

    def get(self, id=None):
        location_detail = Location.query.get_or_404(id)
        return render_template(app.config['UpdateLocationTemplate'], location=location_detail)

    def post(self, id=None):
        try:
            location = Location.query.get_or_404(id)
            if location:
                location.name = request.form['location-name']
                database.session.commit()
        except:
            pass
        finally:
            return redirect('/locations')

class locationDestroyView(MethodView):

    def get(self, id=None):
        location = Location.query.get_or_404(id)
        return render_template(app.config['DeleteLocationTemplate'], location=location)

    def post(self, id=None):
        try:
            location = Location.query.get_or_404(id)
            location.id = id
            if location:
                database.session.delete(location)
                database.session.commit()
        except:
            pass
        finally:
            return redirect('/locations')

class MovementView(MethodView):
    
    def get(self):
        product_list, locations_list, movements_list = Product.query.all(), Location.query.all(),  Movement.query.all()
        return render_template(
                app.config['ViewMovementsTemplate'], 
                products=product_list,
                locations=locations_list,
                movements=movements_list
            )

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
    
    def get(self, id=None):
        product_list, locations_list, movements_list = Product.query.all(), Location.query.all(),  Movement.query.all()
        return render_template(
                app.config['UpdateMovementTemplate'], 
                products=product_list,
                locations=locations_list,
                movements=movements_list
            )

    def post(self, id=None):
        try:
            Movement = Movement.query.get_or_404(id)
            if Movement:
                Movement.destination_location = request.form['destination-location']
                Movement.source_location = request.form['source-location']
                Movement.product = request.form['product']
                Movement.quantity = request.form['quantity']
                database.session.commit()
        except:
            pass
        finally:
            return redirect('/movements')


class MovementDestroyView(MethodView):
    

    def get(self, id=None):
        movement = Movement.query.get_or_404(id)
        return render_template(app.config['DeleteMovementTemplate'], movement=movement)

    def post(self, id=None):
        try:
            movement = Movement.query.filter(Movement.id == id).delete()
            database.session.commit()
        except:
            pass
        finally:
            return redirect('/movements')


class ReportView(MethodView):

    def get(self):
        reports = []
        locations, products = Location.query.all(), Product.query.all()
    
        for location in locations:
            for product in products:
                data = {}
                data["location"] = location.name
                data["product"] = product.name
                total_quantity = Movement.query.filter(
                    Movement.destination_location_id==location.id,
                    Movement.product_id==product.id).from_self(func.sum(Movement.quantity,)).all()
                total_quantity = total_quantity[0][0]
                if total_quantity == None:
                    total_quantity = 0
                data["quantity"] = total_quantity
                reports.append(data)
        return render_template(app.config['ViewReportTemplate'], report=reports)


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
        return '<Movement %r>' % self.id

# END : Database ORM initialization

database.create_all()
app.add_url_rule('/products',view_func=ProductView.as_view('/products'))
app.add_url_rule('/products/<string:id>/update',view_func=ProductUpdateView.as_view('/productsUpdate'))
app.add_url_rule('/products/<string:id>/delete',view_func=ProductDestroyView.as_view('/productsDelete'))
app.add_url_rule('/locations',view_func=LocationsView.as_view('/locations'))
app.add_url_rule('/locations/<string:id>/update',view_func=LocationUpdateView.as_view('locationUpdate'))
app.add_url_rule('/locations/<string:id>/delete',view_func=locationDestroyView.as_view('locationDelete'))
app.add_url_rule('/movements',view_func=MovementView.as_view('movements'))
app.add_url_rule('/movements/<string:id>/update',view_func=MovementUpdateView.as_view('/MovementsUpdate'))
app.add_url_rule('/movements/<string:id>/delete',view_func=MovementDestroyView.as_view('/MovementsDelete'))
app.add_url_rule('/report',view_func=ReportView.as_view('report'))
app.run(debug=True, port=8888)




