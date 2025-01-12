# QPC
*Quantum Pecuniam Coacervatito == How much money am I heaping up?*

A dashboard + tabular data editor made primarily with Dash and plotly, 
which allows you to track your finances in terms of daily expenses, and monthly incomes and budgets.

This hinges on the logging of every single expense you have, so no cheating!

## Setup
* Install the required libraries using requirements.txt or requirements_nv.txt (no specified library versions)
* Add and/or edit .csv data files into the data directory, based on the sample data in data/sample
* Run **app.py** to start the Dash dashboard

## Usage
The **insert_expense.py** script can be used to add a new expense to your **Expenses - Expense_Data.csv** file.
There are different categories for spending, which I usually define as:
1. Savings: Savings (treated as an expense)
2. Rent: Rent (I may change this to a more general "Housing")
3. Grocery: Items bought at grocery stores or for grocery needs
4. Food: Dining, or any food that isn't from groceries
5. Shop: General materialist expenses, clothing, items, games, shopping, etc.
6. RecEnt: Recreation / Entertainment, concerts, events, shows, games, other tickets, etc.
7. TransportationT: Transportation / Travel, gas, airfare, public transit, rideshare, etc.
8. HealthWell: Health / Wellness, doctors, dentists, gyms, therapy, other health expenses
9. Other: Anything else not easy to categorize

In the dashboard itself, there are 5 pages:
1. / (main page)
2. /cells-budget (alternate editor for budget data)
3. /cells-expense (alternate editor for expense data)
4. /cells-income (alternate editor for income data)
5. /worth-dash (quarterly net worth dashboard, WIP)
