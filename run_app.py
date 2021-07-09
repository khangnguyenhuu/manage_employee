import os
import json
from datetime import datetime

from flask import Flask, render_template, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
from sqlalchemy.orm import load_only
from sqlalchemy.sql import text

app = Flask(__name__, template_folder='./templates', static_folder="./static")
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee.sqlite3'
app.config['SECRET_KEY'] = "1234"


db = SQLAlchemy(app)
class Employee(db.Model):
    id = db.Column('employee_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(10))  
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    def __init__(self, name, phone, email, time_in, time_out):
        self.name = name
        self.phone = phone
        self.email = email
        self.time_in = time_in
        self.time_out = time_out


@app.route('/')
@app.route('/home', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        sort_method = request.form['sort_method']
        sort_column = request.form['sort_column']
        if (sort_column == "time_in"):
            if (sort_method == "asc"):
                return render_template('table_content.html', employees=Employee.query.order_by(asc(Employee.time_in)).paginate(per_page=7))

            else:
                return render_template('table_content.html', employees=Employee.query.order_by(desc(Employee.time_in)).paginate(per_page=7))

        else:
            if (sort_method == "asc"):
                return render_template('table_content.html', employees=Employee.query.order_by(asc(Employee.time_out)).paginate(per_page=7))
            else:
                return render_template('table_content.html', employees=Employee.query.order_by(desc(Employee.time_out)).paginate(per_page=7))
    return render_template('table_content.html', employees=Employee.query.paginate(per_page=7))

@app.route('/add_employee', methods=["POST", "GET"])
def add():
    if request.method == "POST":
        if not request.form['name'] or not request.form['phone'] or not request.form['email']:
            flash('Please enter all the fields', 'error')
        else:
            employee = Employee(request.form['name'], request.form['phone'], request.form['email'], datetime.now(), datetime.now())
            db.session.add(employee)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('home'))
        
    return render_template('add_new.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == "GET":
        employee=db.session.query(Employee).filter_by(id=id).first()
        return render_template("add_new.html", employee=employee)
    if request.method == "POST":
        db.session.query(Employee).\
                                    filter_by(id=id).\
                                    update({
                                        "name": request.form['name'],
                                        "phone": request.form['phone'],
                                        "email": request.form['email'],
                                    })
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('add_new.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if request.method == "POST":
        db.session.query(Employee).filter_by(id=id).delete()
        db.session.commit()
        return redirect(url_for('home'))

@app.route('/search', methods=['POST'])
def search():
    if request.method == "POST":
        search_type = request.form['search_type']
        search_value = request.form['search_value'].lower()
        search_value = '%'+search_value+'%'
        if search_type=="name":
            employee = db.session.query(Employee).filter(Employee.name.like(search_value)).all()
        elif search_type=="phone":
            employee = db.session.query(Employee).filter(Employee.phone.like(search_value)).all()
        elif search_type=="email":
            employee = db.session.query(Employee).filter(Employee.email.like(search_value)).all()
        return render_template("table_content.html", employees=employee)


if __name__=="__main__":
    db.create_all()
    app.run(debug=True)