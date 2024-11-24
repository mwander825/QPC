import datetime

# dash and plotly
import dash
from dash import html, dcc
import plotly.express as px

# data
import pandas as pd
pd.options.mode.chained_assignment = None

# register page in app
dash.register_page(__name__,
                   title='Worth Dashboard',
                   name='Worth Dashboard')


class WorthDash:
    def __init__(self):
        self.current_year = pd.Timestamp.now().year
        self.today = datetime.datetime.today()
        self.color_dict = {"Cash": "green",
                           "Asset": "aquamarine",
                           "Liability": "red",
                           "Senex": "purple"}
        self.quarter_dict = {"03/31": "Q1",
                             "06/30": "Q2",
                             "09/31": "Q3",
                             "12/31": "Q4"}
        self.sorted_names = ("Cash", "Asset", "Senex", "Liability")

        # dataframes
        self.df_worth = None
        self.load_data()

    def load_data(self):
        self.df_worth = pd.read_csv(r"data\Quarterly_Worth.csv")

        self.df_worth["Date"] = pd.to_datetime(self.df_worth["Date"])
        self.df_worth["Year-Month"] = pd.to_datetime(self.df_worth["Date"]).dt.to_period('M')
        self.df_worth["Month-Year"] = self.df_worth["Year-Month"].dt.strftime("%b-%Y")
        
        self.df_worth["Quarter"] = self.df_worth["Date"].apply(lambda dt: f"{dt.year} {self.quarter_dict.get(dt.strftime('%m/%d'))}")

        self.df_worth["Type"] = self.df_worth["Type"].astype("category")
        self.df_worth["Amount"] = self.df_worth["Amount"].astype(float)

    def create_bar_worth_fig(self):
        month_group_sums = self.df_worth.groupby(["Quarter", "Type"], observed=False)["Amount"].sum().round(
            2).reindex(
            self.sorted_names, level='Type').reset_index()
        #month_group_sums["Month-Year"] = month_group_sums["Date"].dt.strftime("%b-%Y")

        # create main time-series worth figure
        fig = px.bar(month_group_sums, x='Quarter', y='Amount', color='Type', barmode='stack',
                     color_discrete_map=self.color_dict,
                     hover_data={'Type': False,
                                 'Quarter': False},
                     labels={'Amount': "Amount ($)"})


        # format hover values to two decimal point floats
        fig.update_traces(hovertemplate="%{y:$.2f}<extra></extra>")

        # make y-max 500 more than the highest worth quarter
        fig.update_layout(hovermode="x unified")
        return fig

# kind of like a dash page reload callback when used with multipage app
# if you just create a "layout" variable, it doesn't reload
def layout():
    global worth_dash
    worth_dash = WorthDash()

    bar_worth_fig = worth_dash.create_bar_worth_fig()

    hlayout = html.Div(children=[
        html.H1(children="Worth"),

        html.Div(children=[
            html.H2("""Quarterly Worth"""),

            dcc.Graph(
                id='worth-quarterly',
                figure=bar_worth_fig
            ),
            ])
    ])
    return hlayout
