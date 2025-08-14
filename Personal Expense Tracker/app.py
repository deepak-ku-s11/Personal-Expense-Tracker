from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime
import os
import json

app = Flask(__name__)
FILE_NAME = "expenses.csv"
CATEGORY_FILE = "categories.csv"

if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Item", "Category", "Amount"])

if not os.path.exists(CATEGORY_FILE):
    with open(CATEGORY_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        for cat in ["Food","Transport","Bills","Entertainment","Shopping","Other"]:
            writer.writerow([cat])

# Read categories
def get_categories():
    categories = []
    with open(CATEGORY_FILE, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                categories.append(row[0])
    return categories

# Home / Add Expense
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form.get('item')
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date') or datetime.today().strftime('%d-%m-%Y')

        if not item or not category or not amount:
            return "All fields except date are required!"

        try:
            amount = float(amount)
        except ValueError:
            return "Amount must be a number!"

        try:
            datetime.strptime(date, '%d-%m-%Y')
        except ValueError:
            date = datetime.today().strftime('%d-%m-%Y')

        with open(FILE_NAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, item, category, amount])

        return redirect('/')

    # Read expenses
    expenses = []
    with open(FILE_NAME, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            expenses.append(row)

    # Chart data
    category_data = {}
    month_data = {}
    for date_str, _, category, amount in expenses:
        amount = float(amount)
        category_data[category] = category_data.get(category,0)+amount
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        month = date_obj.strftime('%B %Y')
        month_data[month] = month_data.get(month,0)+amount

    return render_template('index.html', expenses=expenses, categories=get_categories(),
                           category_data=json.dumps(category_data),
                           month_data=json.dumps(month_data))

# Add new category
@app.route('/add_category', methods=['POST'])
def add_category():
    new_cat = request.form.get('new_category')
    if new_cat:
        categories = get_categories()
        if new_cat not in categories:
            with open(CATEGORY_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([new_cat])
    return redirect('/')

# Summary by category
@app.route('/summary')
def summary():
    summary = {}
    with open(FILE_NAME, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for _, _, category, amount in reader:
            amount = float(amount)
            summary[category] = summary.get(category,0)+amount
    return render_template('summary.html', summary=summary)

# Summary by month
@app.route('/monthly')
def monthly():
    monthly = {}
    with open(FILE_NAME, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for date_str, _, _, amount in reader:
            amount = float(amount)
            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            month = date_obj.strftime('%B %Y')
            monthly[month] = monthly.get(month,0)+amount
    return render_template('monthly.html', monthly=monthly)

if __name__ == '__main__':
    app.run(debug=True)