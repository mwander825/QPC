import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# dash and plotly
import dash
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

# data
import pandas as pd
from datetime import date
import calendar
pd.options.mode.chained_assignment = None

# register page in app
dash.register_page(__name__, path="/",
                   title='Money Dashboard',
                   name='Money Dashboard')


class MoneyDash:
    def __init__(self):
        self.current_year = pd.Timestamp.now().year
        self.today = datetime.datetime.today()
        self.color_dict = {"Savings": "green",
                           "Rent": "purple",
                           "Utilities": "pink",
                           "Grocery": "yellow",
                           "Food": "orange",
                           "Shop": "red",
                           "RecEnt": "cyan",
                           "TransportationT": "Brown",
                           "HealthWell": "cornsilk",
                           "Other": "gray"}

        self.sorted_names = ("Savings", "Rent", "Utilities", "Grocery", "Food",
                             "Shop", "RecEnt", "TransportationT", "HealthWell", "Other")

        self.DOW_dict = {"Monday": 0,
                         "Tuesday": 1,
                         "Wednesday": 2,
                         "Thursday": 3,
                         "Friday": 4,
                         "Saturday": 5,
                         "Sunday": 6}

        self.month_list = ['January', 'February', 'March', 'April',
                           'May', 'June', 'July', 'August',
                           'September', 'October', 'November', "December"]

        self.month_dict = {month: idx + 1 for idx, month in enumerate(self.month_list)}

        self.necesse_dict = {"Rent": "Needs",
                             "Utilities": "Needs",
                             "Grocery": "Needs",
                             "Food": "Needs",
                             "Savings": "Savings",
                             "Shop": "Wants",
                             "RecEnt": "Wants",
                             "TransportationT": "Wants",
                             "HealthWell": "Needs",
                             "Other": "Wants"}

        self.necesse_color_dict = {"Needs": "purple",
                                   "Savings": "green",
                                   "Wants": "red"}

        # month years
        self.month_year_list = None

        # dataframes
        self.df_expense, self.df_income, self.df_budget = None, None, None
        self.df_expense_group_sum, \
            self.df_income_group_sum, \
            self.df_income_now_group_sum, \
            self.df_budget_group_sum = None, None, None, None
        self.df_all_group_sum = None
        self.load_data()

        # years
        self.year_list = list(self.df_expense["Year"].sort_values(ascending=False).unique())

    def load_data(self):
        # Load data
        self.df_expense = pd.read_csv(r"data\Expenses - Expense_Data.csv", dtype={"Name": "object",
                                                                                  "Amount": "float",
                                                                                  "Type": "category",
                                                                                  "Date": "object"})
        self.df_income = pd.read_csv(r"data\Expenses - Income_Data.csv", dtype={"Name": "object",
                                                                                "Amount": "float",
                                                                                "Type": "category",
                                                                                "Date": "object"})
        self.df_budget = pd.read_csv(r"data\Expenses - Budget_Data.csv", dtype={"Name": "object",
                                                                                "Amount": "float",
                                                                                "Type": "category",
                                                                                "Date": "object"})
        # expense data
        self.df_expense["Date"] = pd.to_datetime(self.df_expense["Date"])
        self.df_expense["Type"] = self.df_expense["Type"].astype("category")
        self.df_expense["Year-Month"] = self.df_expense["Date"].dt.to_period('M')
        self.df_expense["Month-Year"] = self.df_expense["Year-Month"].dt.strftime("%b-%Y")
        self.df_expense["Year"] = self.df_expense["Date"].dt.year
        self.df_expense["Day"] = self.df_expense["Date"].dt.to_period('D')
        self.df_expense["FOM"] = self.df_expense["Month-Year"].apply(lambda d: datetime.datetime.strptime(d, "%b-%Y").date())
        self.df_expense["Necesse"] = self.df_expense["Type"].apply(lambda t: self.necesse_dict.get(t))
        self.df_expense_group_sum = self.df_expense.rename(columns={"Amount": "Expense_Total"}) \
            .groupby(["Year-Month", "Month-Year", "FOM", "Year"], as_index=False, observed=False)["Expense_Total"].sum()

        # set month_year list
        self.month_year_list = list(self.df_expense["Month-Year"].unique())

        # income data
        self.df_income["Date"] = pd.to_datetime(self.df_income["Date"])
        self.df_income["Year-Month"] = pd.to_datetime(self.df_income["Date"]).dt.to_period('M')
        self.df_income["Month-Year"] = self.df_income["Year-Month"].dt.strftime("%b-%Y")
        self.df_income["Year"] = self.df_income["Date"].dt.year
        self.df_income["FOM"] = self.df_income["Month-Year"].apply(lambda d: datetime.datetime.strptime(d, "%b-%Y").date())
        self.df_income_group_sum = self.df_income.rename(columns={"Amount": "Income_Total"}) \
            .groupby(["Year-Month", "Month-Year", "FOM", "Year"], as_index=False, observed=False)["Income_Total"].sum()
        self.df_income_now_group_sum = self.df_income[self.df_income["Date"] <= self.today] \
            .rename(columns={"Amount": "Income_Now"}) \
            .groupby(["Year-Month", "Month-Year", "FOM", "Year"], as_index=False, observed=False)["Income_Now"].sum()

        # budget data
        self.df_budget["Date"] = pd.to_datetime(self.df_budget["Date"])
        self.df_budget["Year-Month"] = pd.to_datetime(self.df_budget["Date"]).dt.to_period('M')
        self.df_budget["Month-Year"] = self.df_budget["Year-Month"].dt.strftime("%b-%Y")
        self.df_budget["Year"] = self.df_budget["Date"].dt.year
        self.df_budget["FOM"] = self.df_budget["Month-Year"].apply(lambda d: datetime.datetime.strptime(d, "%b-%Y").date())
        self.df_budget_group_sum = self.df_budget.rename(columns={"Amount": "Budget_Total"}) \
            .groupby(["Year-Month", "Month-Year", "FOM", "Year"], as_index=False, observed=False)["Budget_Total"].sum()

        # combine all month sums (expense, income, budget)
        self.df_all_group_sum = pd.concat((self.df_expense_group_sum,
                                           self.df_income_group_sum["Income_Total"],
                                           self.df_income_now_group_sum["Income_Now"],
                                           self.df_budget_group_sum["Budget_Total"]),
                                           axis=1)

    def create_range_spend_figs(self, start_date: datetime.date, end_date: datetime.date, freq: str = 'Monthly'):
        if freq == 'Monthly':
            # clip'd
            df_all_group_sum = self.df_all_group_sum[self.df_all_group_sum["FOM"].between(start_date, end_date)]
            month_expense_sums = self.df_expense_group_sum[self.df_expense_group_sum["FOM"].between(start_date, end_date)]
            month_expense_sums["Month-Year"] = month_expense_sums["Year-Month"].dt.strftime("%b-%Y")

            # group by type and aggregate for each month
            month_group_sums = self.df_expense[self.df_expense["FOM"].between(start_date, end_date)].groupby(["Year-Month", "Type"], observed=False)["Amount"].sum().round(2).reindex(
                self.sorted_names, level='Type').reset_index()
            month_group_sums["Month-Year"] = month_group_sums["Year-Month"].dt.strftime("%b-%Y")

            # create main time-series expense figure
            fig = px.bar(month_group_sums, x='Month-Year', y='Amount', color='Type', barmode='stack',
                         color_discrete_map=self.color_dict,
                         hover_data={'Type': False,
                                     'Month-Year': False},
                         labels={'Amount': "Amount ($)"})

            # format hover values to two decimal point floats
            fig.update_traces(hovertemplate="%{y:$.2f}<extra></extra>")

            # add time-series scatter traces for income and budget over time
            # dashed lines with markers representing income and budget boundaries
            fig.add_trace(go.Scatter(x=df_all_group_sum["Month-Year"], y=df_all_group_sum["Income_Now"],
                                     mode='lines+markers',
                                     name='Present Income', line=dict(color='blueviolet', width=4, dash='dash'),
                                     hovertemplate="%{y:$.2f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=df_all_group_sum["Month-Year"], y=df_all_group_sum["Income_Total"],
                                     mode='lines+markers',
                                     name='Total Income', line=dict(color='blue', width=4, dash='dash'),
                                     hovertemplate="%{y:$.2f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=df_all_group_sum["Month-Year"], y=df_all_group_sum["Budget_Total"],
                                     mode='lines+markers',
                                     name='Budget', line=dict(color='skyblue', width=4, dash='dash'),
                                     hovertemplate="%{y:$.2f}<extra></extra>"))

            # iterate over month sums for all three amounts (expense, income, budget)
            for idx, row in df_all_group_sum.iterrows():
                idx = int(idx)
                year_month, month_year, fom = row[0:3]
                month_spend_total, month_income_total, month_present_income_total, month_budget_total = row[-4:]

                # calculate the remaining days of the current month
                days_remaining = pd.Period(self.today,
                                           freq='M').end_time.date().day - self.today.day if self.today.month == year_month.month else 0

                fig.add_trace(go.Scatter(x=[month_year, month_year],
                                         y=[month_spend_total, month_income_total],
                                         mode='lines',
                                         line=dict(color='black', width=2),
                                         name="Surplus",
                                         hoverinfo="skip",
                                         hovertext=f"{round(month_income_total - month_spend_total, 2)}",
                                         hovertemplate=f"${round(month_income_total - month_spend_total, 2)}<extra></extra>",
                                         legendgroup="Surplus",
                                         showlegend=False if idx > 0 else True))
                fig.add_trace(go.Scatter(x=[month_year, month_year],
                                         y=[month_spend_total, month_budget_total],
                                         mode='lines',
                                         line=dict(color='darkgray', width=2),
                                         name="Left",
                                         hoverinfo="skip",
                                         hovertext=f"{round(month_budget_total - month_spend_total, 2)} ({days_remaining})",
                                         hovertemplate=f"${round(month_budget_total - month_spend_total, 2)} ({days_remaining})<extra></extra>",
                                         legendgroup="Left",
                                         showlegend=False if idx > 0 else True))

            # fig.add_hrect(y0=m_expenses, y1=m_income, line_width=0, fillcolor="red", opacity=0.1)

            # make y-max 500 more than the highest income month
            fig.update_layout(yaxis_range=(0, df_all_group_sum["Income_Total"].max() + 500), hovermode="x unified")

            # create cumulative sum surplus figure over time
            surplus_y = (df_all_group_sum["Income_Total"] - df_all_group_sum[
                "Expense_Total"]).dropna().cumsum()
            surplus_x = month_expense_sums["Month-Year"].unique()
            surplus_fig = px.bar(x=surplus_x, y=surplus_y, labels={'x': 'Month-Year',
                                                                   'y': "Surplus ($)"})
            # add line with markers to tops of bars
            surplus_fig.add_trace(
                go.Scatter(x=surplus_x, y=surplus_y, mode='lines+markers', line=dict(color='green', width=2),
                           showlegend=False))
            surplus_fig.update_layout()

        elif freq == 'Yearly':
            # clip'd
            df_all_group_sum = self.df_all_group_sum[self.df_all_group_sum["FOM"].between(start_date, end_date)]
            year_expense_sums = self.df_expense_group_sum[self.df_expense_group_sum["FOM"].between(start_date, end_date)]

            # group by year
            df_all_group_sum = df_all_group_sum.groupby("Year", as_index=False, observed=False)[["Expense_Total",  "Income_Total",  "Budget_Total"]].sum()
            year_expense_sums = year_expense_sums.groupby("Year", as_index=False, observed=False)["Expense_Total"].sum()

            # group by type and aggregate for each year
            year_group_sums = self.df_expense[self.df_expense["FOM"].between(start_date, end_date)].groupby(["Year", "Type"], observed=False)["Amount"].sum().round(2).reindex(
                self.sorted_names, level='Type').reset_index()

            # fix integer axis?
            year_group_sums["Year"] = year_group_sums["Year"].astype(int).astype(str)
            year_expense_sums["Year"] = year_expense_sums["Year"].astype(int).astype(str)
            df_all_group_sum["Year"] = df_all_group_sum["Year"].astype(int).astype(str)

            # create main time-series expense figure
            fig = px.bar(year_group_sums, x='Year', y='Amount', color='Type', barmode='stack',
                         color_discrete_map=self.color_dict,
                         hover_data={'Type': False,
                                     'Year': False},
                         labels={'Amount': "Amount ($)"})

            # format hover values to two decimal point floats
            fig.update_traces(hovertemplate="%{y:$.2f}<extra></extra>")

            # add time-series scatter traces for income and budget over time
            # dashed lines with markers representing income and budget boundaries
            fig.add_trace(go.Scatter(x=df_all_group_sum["Year"], y=df_all_group_sum["Income_Total"],
                                     mode='lines+markers',
                                     name='Income', line=dict(color='blue', width=4, dash='dash'),
                                     hovertemplate="%{y:$.2f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=df_all_group_sum["Year"], y=df_all_group_sum["Budget_Total"],
                                     mode='lines+markers',
                                     name='Budget', line=dict(color='skyblue', width=4, dash='dash'),
                                     hovertemplate="%{y:$.2f}<extra></extra>"))

            fig.update_layout(yaxis_range=(0, df_all_group_sum["Income_Total"].max() + 500), hovermode="x unified")

            # for now...
            # create cumulative sum surplus figure over time
            surplus_y = (df_all_group_sum["Income_Total"] - df_all_group_sum[
                "Expense_Total"]).dropna().cumsum()
            surplus_x = year_expense_sums["Year"].unique()
            surplus_fig = px.bar(x=surplus_x, y=surplus_y, labels={'x': 'Year',
                                                                   'y': "Surplus ($)"})
            # add line with markers to tops of bars
            surplus_fig.add_trace(
                go.Scatter(x=surplus_x, y=surplus_y, mode='lines+markers', line=dict(color='green', width=2),
                           showlegend=False))
            surplus_fig.update_layout()

        elif freq == 'Weekly':
            surplus_fig = {}
            raise NotImplementedError
        else:
            raise ValueError("Value must be one of {'Monthly', 'Yearly', 'Weekly'}")

        return fig, surplus_fig

    def create_ratios_fig(self, start_date, end_date):
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        dff_month = self.df_expense[self.df_expense["Date"].between(start_date, end_date)]
        month_group_sums = dff_month.groupby("Necesse", observed=False)["Amount"].sum().round(2).reset_index()

        fig = px.pie(month_group_sums, values='Amount', names='Necesse', color='Necesse', color_discrete_map=self.necesse_color_dict,
                     hole=0.5)

        return fig

    def create_cat_spend_fig(self, start_date, end_date):
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        dff_month = self.df_expense[self.df_expense["Date"].between(start_date, end_date)]

        cat_group_sums = dff_month.groupby("Type", as_index=False, observed=False)["Amount"].sum()

        # color_dict_so_far = {key: value for key, value in color_dict.items() if key in cat_group_sums["Type"].values}

        fig = px.bar(cat_group_sums, x="Type", y='Amount', color='Type', hover_data='Amount',
                     color_discrete_map=self.color_dict,
                     category_orders={"Type": self.sorted_names})
        sel = ['Rent', "Savings", "Utilities"]
        fig.update_traces(selector=lambda t: t.name in sel, visible='legendonly')

        return fig

    def create_name_spend_fig(self, start_date, end_date):
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        dff_month = self.df_expense[self.df_expense["Date"].between(start_date, end_date)]
        dff_month["Type"] = dff_month["Type"].astype("object")

        #dff_month = self.df_expense.loc[self.df_expense.loc[:, "Year-Month"] == month, :]
        # dff_month.loc[:, "Type"] = dff_month.loc[:, "Type"].astype(
        #     "object")  # weird error if one of the types has no entries as category
        name_group_sums = dff_month.groupby(["Name", "Type"], as_index=False, observed=False)["Amount"].sum()
        name_group_sums = name_group_sums[name_group_sums["Amount"] != 0.0].sort_values("Amount",
                                                                                        ascending=False).reset_index(
            drop=True)
        # color_dict_so_far = {key: value for key, value in color_dict.items() if key in name_group_sums["Type"].values}

        fig = px.bar(name_group_sums, x="Name", y="Amount", color='Type', hover_data='Amount',
                     color_discrete_map=self.color_dict,
                     category_orders={"Name": tuple(name_group_sums["Name"].values)})
        sel = ['Rent', "Savings", "Utilities"]
        fig.update_traces(selector=lambda t: t.name in sel, visible='legendonly')

        return fig

    def create_dow_spend_fig(self, start_date: datetime.date, end_date: datetime.date):
        # if month is None:
        #     month = self.today.strftime("%Y-%m")
        #dff_month = self.df_expense[self.df_expense["Year-Month"] == month]
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        dff_month = self.df_expense[self.df_expense["Date"].between(start_date, end_date)]
        dff_month["DOW"] = dff_month["Date"].dt.strftime("%A")
        day_group_sums = dff_month.groupby(["DOW", "Type"], observed=False)["Amount"].sum().round(2).reindex(
                self.sorted_names, level='Type').reset_index()

        fig = px.bar(day_group_sums, x='DOW', y='Amount', color='Type', barmode='stack',
                     color_discrete_map=self.color_dict,
                     hover_data={'Type': False,
                                 'DOW': False},
                     labels={'Amount': "Amount ($)"})

        sel = ['Rent', "Savings", "Utilities"]
        fig.update_traces(selector=lambda t: t.name in sel, visible='legendonly')

        fig.update_layout(hovermode="x unified")
        fig.update_traces(hovertemplate="%{y:$.2f}<extra></extra>")
        fig.update_xaxes(type='category', categoryorder='array', categoryarray=list(self.DOW_dict.keys()))

        return fig

    def create_pie_spend_fig(self, start_date: datetime.date, end_date: datetime.date):
        # if month is None:
        #     month = self.today.strftime("%Y-%m")
        # dff_month = self.df_expense[self.df_expense["Year-Month"] == month]
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        dff_month = self.df_expense[self.df_expense["Date"].between(start_date, end_date)]
        month_expense_sums = dff_month.groupby(["Year-Month"], as_index=False, observed=False)["Amount"].sum().round(2)
        month_group_sums = dff_month.groupby(["Year-Month", "Type"], observed=False)["Amount"].sum().round(2).reindex(self.sorted_names,
                                                                                                      level='Type').reset_index()
        month_group_sums["Month-Year"] = month_group_sums["Year-Month"].dt.strftime("%b-%Y")
        month_expense_sums["Month-Year"] = month_expense_sums["Year-Month"].dt.strftime("%b-%Y")
        fig = px.pie(month_group_sums, values='Amount', names='Type', color='Type', color_discrete_map=self.color_dict, hole=0.5)

        return fig

    def create_total_spend_fig(self):
        dff_income = self.df_income[self.df_income["Date"] <= self.today]
        dff_expense = self.df_expense[self.df_expense["Date"] <= self.today]

        # will be "off" for a month if all paydays haven't passed
        income_sum = dff_income["Amount"].sum().round(2)
        expense_sum_all = dff_expense["Amount"].sum().round(2)
        expense_sum = dff_expense[dff_expense["Type"] != "Savings"]["Amount"].sum().round(2)
        saving_sum = dff_expense[dff_expense["Type"] == "Savings"]["Amount"].sum().round(2)

        fig = px.bar(x=(saving_sum + (income_sum - expense_sum_all), expense_sum, income_sum),
                     y=('Savings', 'Expenses', 'Income'),
                     labels={'x': 'Amount', 'y': 'Type'},
                     orientation='h')
        return fig


# kind of like a dash page reload callback when used with multipage app
# if you just create a "layout" variable, it doesn't reload
def layout():
    global money_dash
    money_dash = MoneyDash()

    # month list and dict
    # year list
    month_list, month_dict = money_dash.month_list, money_dash.month_dict
    month_year_list = money_dash.month_year_list
    year_list = list(map(str, money_dash.year_list))

    # minimum years
    minimum_year, maximum_year = str(min(money_dash.year_list)), str(max(money_dash.year_list))

    # start and end moy
    start_date = datetime.datetime.strptime(f"January-{minimum_year}", "%B-%Y").date()
    end_date = datetime.datetime.strptime(f"December-{maximum_year}", "%B-%Y").date()

    # minimum and maximum dates for DatePickerRange
    minimum_date = money_dash.df_budget["Date"].min().date()

    expense_max_date = money_dash.df_expense["Date"].max().date()
    maximum_date = date(expense_max_date.year,
                        expense_max_date.month,
                        calendar.monthrange(expense_max_date.year, expense_max_date.month)[-1])

    tonight_tonight = money_dash.today
    _, today_max = calendar.monthrange(tonight_tonight.date().year, tonight_tonight.date().month)
    today_min = date(tonight_tonight.year, tonight_tonight.month, 1)
    today_max = date(tonight_tonight.year, tonight_tonight.month, today_max)

    range_spend_fig, range_surplus_fig = money_dash.create_range_spend_figs(start_date, end_date)
    range_ratios_fig = money_dash.create_ratios_fig(minimum_date, maximum_date)
    cat_spend_fig = money_dash.create_cat_spend_fig(minimum_date, maximum_date)
    name_spend_fig = money_dash.create_name_spend_fig(minimum_date, maximum_date)
    pie_spend_fig = money_dash.create_pie_spend_fig(minimum_date, maximum_date)
    dow_spend_fig = money_dash.create_dow_spend_fig(minimum_date, maximum_date)
    total_spend_fig = money_dash.create_total_spend_fig()

    hlayout = html.Div(children=[
        html.H1(children="Budgeting"),

        html.Div(children=[
            html.H2("""Spending Over Time (Stacked)"""),
            html.Div(children=[
                dcc.Dropdown(options=year_list, value=minimum_year, clearable=False, id='spending-year-min-drop', style={'width': "80%"}),
                dcc.Dropdown(options=year_list, value=maximum_year, clearable=False, id='spending-year-max-drop', style={'width': "80%"}),
                dcc.Dropdown(options=month_list, value='January', clearable=False, id='spending-month-min-drop', style={'width': "100%"}),
                dcc.Dropdown(options=month_list, value='December', clearable=False, id='spending-month-max-drop', style={'width': "100%"}),
                dcc.Dropdown(options=['Yearly', 'Monthly', 'Weekly'], value="Monthly", clearable=False, id='spending-frequency-drop', style={'width': "100%"}),
                dcc.Dropdown(options=month_year_list, value=None, clearable=True, id='spending-month-iso-drop', style={'width': "100%", "padding-left": "20px"}),
            ], style={'display': 'flex', 'width': '66%'}),

            dcc.Graph(
                id='spending-range',
                figure=range_spend_fig
            ),
            html.H2("""Surplus Over Time"""),
            dcc.Graph(
                id='surplus-range',
                figure=range_surplus_fig
            )
        ]),
        html.Div(children=[
            html.H2("""Ratios (Needs : Savings : Wants)"""),
            html.Div(children=[
                dcc.DatePickerRange(
                id='ratios-date-picker-range',
                start_date=today_min,
                min_date_allowed=minimum_date,
                max_date_allowed=maximum_date,
                end_date=today_max
            ),
            dcc.Dropdown(options=month_year_list, value=None, clearable=True, id='ratios-month-iso-drop', style={'width': "33%"}),
                ], style={'display': 'block', 'width': '100%'}),
            dcc.Graph(
                id='spending-ratios',
                figure=range_ratios_fig
            ),
        ]),
        html.Div(children=[
            html.H2("""Total Income, Spend, and Savings"""),
            dcc.Graph(
                id='total-spend',
                figure=total_spend_fig
            ),
            html.H2("""Spending by Category (Unstacked)"""),
            html.Div(children=[
                dcc.DatePickerRange(
                id='cat-date-picker-range',
                start_date=today_min,
                min_date_allowed=minimum_date,
                max_date_allowed=maximum_date,
                end_date=today_max
                ),
                dcc.Dropdown(options=month_year_list, value=None, clearable=True, id='cat-month-iso-drop',
                             style={'width': "33%"})
            ], style={'display': 'block', 'width': '100%'}),
            dcc.Graph(
                id='spending-category',
                figure=cat_spend_fig
            ),
        ]),
        html.Div(children=[
            html.H2("""Spending by Name"""),
            html.Div(children=[
                dcc.DatePickerRange(
                id='name-date-picker-range',
                start_date=today_min,
                min_date_allowed=minimum_date,
                max_date_allowed=maximum_date,
                end_date=today_max
            ),
                dcc.Dropdown(options=month_year_list, value=None, clearable=True, id='name-month-iso-drop',
                             style={'width': "33%"})
            ], style={'display': 'block', 'width': '100%'}),
            dcc.Graph(
                id='spending-name',
                figure=name_spend_fig,
                responsive=True,
                style={'height': '85vh'}  # when names get too long
            ),
        ]),
        html.Div(children=[
            html.H2("""Spending by DOW"""),
            html.Div(children=[
            dcc.DatePickerRange(
                id='dow-date-picker-range',
                start_date=today_min,
                min_date_allowed=minimum_date,
                max_date_allowed=maximum_date,
                end_date=today_max
            ),
                dcc.Dropdown(options=month_year_list, value=None, clearable=True, id='dow-month-iso-drop',
                             style={'width': "33%"})
            ], style={'display': 'block', 'width': '100%'}),
            dcc.Graph(
                id='spending-dow',
                figure=dow_spend_fig
            ),
        ]),
        html.Div(children=[
            html.H2("""Spending Pie"""),
            html.Div(children=[
                dcc.DatePickerRange(
                id='pie-date-picker-range',
                start_date=today_min,
                min_date_allowed=minimum_date,
                max_date_allowed=maximum_date,
                end_date=today_max
            ),
                dcc.Dropdown(options=month_year_list, value=None, clearable=True, id='pie-month-iso-drop',
                             style={'width': "33%"})
            ], style={'display': 'block', 'width': '100%'}),
            dcc.Graph(
                id='spending-pie',
                figure=pie_spend_fig
            )
        ])
    ])
    return hlayout


# callbacks
@callback(
      Output('spending-category', 'figure'),
      Input('cat-date-picker-range', 'start_date'),
      Input('cat-date-picker-range', 'end_date'),
      Input('cat-month-iso-drop', 'value'))
def update_cat_figure(start_date, end_date, month_iso):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if month_iso is not None and isinstance(month_iso, str):
        iso_date = datetime.datetime.strptime(month_iso, "%b-%Y").date()
        iso_month, iso_year = iso_date.month, iso_date.year
        _, last = calendar.monthrange(iso_year, iso_month)
        start_date = datetime.datetime(iso_year, iso_month, 1).date()
        end_date = datetime.datetime(iso_year, iso_month, last).date()
    return money_dash.create_cat_spend_fig(start_date, end_date)


@callback(
      Output('spending-name', 'figure'),
      Input('name-date-picker-range', 'start_date'),
      Input('name-date-picker-range', 'end_date'),
      Input('name-month-iso-drop', 'value'))
def update_name_figure(start_date, end_date, month_iso):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if month_iso is not None and isinstance(month_iso, str):
        iso_date = datetime.datetime.strptime(month_iso, "%b-%Y").date()
        iso_month, iso_year = iso_date.month, iso_date.year
        _, last = calendar.monthrange(iso_year, iso_month)
        start_date = datetime.datetime(iso_year, iso_month, 1).date()
        end_date = datetime.datetime(iso_year, iso_month, last).date()
    return money_dash.create_name_spend_fig(start_date, end_date)


@callback(
      Output('spending-dow', 'figure'),
      Input('dow-date-picker-range', 'start_date'),
      Input('dow-date-picker-range', 'end_date'),
      Input('dow-month-iso-drop', 'value'))
def update_dow_figure(start_date, end_date, month_iso):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if month_iso is not None and isinstance(month_iso, str):
        iso_date = datetime.datetime.strptime(month_iso, "%b-%Y").date()
        iso_month, iso_year = iso_date.month, iso_date.year
        _, last = calendar.monthrange(iso_year, iso_month)
        start_date = datetime.datetime(iso_year, iso_month, 1).date()
        end_date = datetime.datetime(iso_year, iso_month, last).date()
    return money_dash.create_dow_spend_fig(start_date, end_date)


@callback(
      Output('spending-pie', 'figure'),
      Input('pie-date-picker-range', 'start_date'),
      Input('pie-date-picker-range', 'end_date'),
      Input('pie-month-iso-drop', 'value'))
def update_pie_figure(start_date, end_date, month_iso):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if month_iso is not None and isinstance(month_iso, str):
        iso_date = datetime.datetime.strptime(month_iso, "%b-%Y").date()
        iso_month, iso_year = iso_date.month, iso_date.year
        _, last = calendar.monthrange(iso_year, iso_month)
        start_date = datetime.datetime(iso_year, iso_month, 1).date()
        end_date = datetime.datetime(iso_year, iso_month, last).date()
    return money_dash.create_pie_spend_fig(start_date, end_date)


@callback(
      Output('spending-ratios', 'figure'),
      Input('ratios-date-picker-range', 'start_date'),
      Input('ratios-date-picker-range', 'end_date'),
      Input('ratios-month-iso-drop', 'value'))
def update_ratios_figure(start_date, end_date, month_iso):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if month_iso is not None and isinstance(month_iso, str):
        iso_date = datetime.datetime.strptime(month_iso, "%b-%Y").date()
        iso_month, iso_year = iso_date.month, iso_date.year
        _, last = calendar.monthrange(iso_year, iso_month)
        start_date = datetime.datetime(iso_year, iso_month, 1).date()
        end_date = datetime.datetime(iso_year, iso_month, last).date()
    return money_dash.create_ratios_fig(start_date, end_date)


# multi-output callbacks?
@callback(
    Output('spending-range', 'figure'),
    Output('surplus-range', 'figure'),
    Input('spending-year-min-drop', 'value'),
    Input('spending-year-max-drop', 'value'),
    Input('spending-month-min-drop', 'value'),
    Input('spending-month-max-drop', 'value'),
    Input('spending-frequency-drop', 'value'),
    Input('spending-month-iso-drop', 'value'))
def update_spending_figure(start_year, end_year, start_month, end_month, frequency, month_iso):
    start_date = datetime.datetime.strptime(f"{start_month}-{start_year}", "%B-%Y").date()
    end_date = datetime.datetime.strptime(f"{end_month}-{end_year}", "%B-%Y").date()
    if frequency == "Monthly" and (month_iso is not None and isinstance(month_iso, str)):
        iso_date = datetime.datetime.strptime(month_iso, "%b-%Y").date()
        start_date, end_date = (iso_date, iso_date)
    return money_dash.create_range_spend_figs(start_date, end_date, frequency)
