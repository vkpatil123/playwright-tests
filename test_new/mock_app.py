from flask import Flask, render_template, request, redirect, url_for, session
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
app.secret_key = 'supersecret'

# Fake product data
products = [
    {"name": f"Product {i}", "sku": f"SKU{i:04d}", "quantity": str(i*3), "price": f"${i*10:.2f}"}
    for i in range(1, 51)
]

@app.route('/')
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "test" and password == "test":
            session["user"] = username
            return redirect(url_for("dashboard"))
        return "Invalid credentials", 403
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route('/tools')
def tools():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("tools.html")

@app.route('/tools/data')
def tools_data():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("tools_data.html")

@app.route('/tools/data/inventory')
def inventory():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("inventory.html")

@app.route('/tools/data/inventory/products')
def product_table_nested():  # Changed function name
    if "user" not in session:
        return redirect(url_for("login"))

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    pagination = Pagination(page=page, total=len(products), per_page=per_page, record_name='products')
    return render_template("products.html", products=products[start:end], pagination=pagination)

@app.route('/products')
def product_table():  # Keep this name for the direct route
    if "user" not in session:
        return redirect(url_for("login"))

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    pagination = Pagination(page=page, total=len(products), per_page=per_page, record_name='products')
    return render_template("products.html", products=products[start:end], pagination=pagination)
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
