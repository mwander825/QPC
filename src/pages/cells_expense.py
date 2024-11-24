import dash

from dash import dash_table, html, Input, Output, State, callback
import dash_daq as daq
import datetime

import pandas as pd
import os

# register page in app
dash.register_page(__name__,
                   title='Expense Data Editor',
                   name='Expense Data Editor')

# Load data
file_dir = "data"
file_name = "Expenses - Expense_Data"
file_path = os.path.join(file_dir, file_name) + ".csv"


def layout():
    df_expense = pd.read_csv(file_path, dtype={"Name": "object",
                                               "Amount": "float",
                                               "Type": "category",
                                               "Date": "object"})

    # convert revert
    df_expense["Date"] = pd.to_datetime(df_expense["Date"])
    df_expense = df_expense.sort_values("Date")
    df_expense["Date"] = df_expense["Date"].dt.strftime("%m/%d/%Y")

    cols = df_expense.columns

    page_layout = html.Div([
        dash_table.DataTable(
            id='adding-rows-table-e',
            style_cell={'textAlign': 'left'},
            style_data={
                    'color': 'black',
                    'backgroundColor': 'white'
                },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(220, 220, 220)',
                }
                ],
            style_header={
                'backgroundColor': 'rgb(210, 210, 210)',
                'color': 'black',
                'fontWeight': 'bold'
                },
            columns=([{'id': c, 'name': c} if c != "Type" else {'id': c, 'name': c, 'presentation': 'dropdown'} for c in cols]),
            data=df_expense.to_dict('records'),
            dropdown={
                'Type': {
                    'clearable': False,
                    'options': [
                        {'label': i, 'value': i}
                        for i in df_expense['Type'].unique()
                    ]
                }},
            editable=True,
            fill_width=False,
            row_deletable=True,
            page_size=500
        ),
        html.Div(id='occultum-sum-e', hidden=True),
        html.Div([
            html.Button('Add Row', id='editing-rows-button-e', n_clicks=0),
            html.Button('Save Changes', id='save-button-e', n_clicks=0),
            daq.BooleanSwitch(id='backup-switch-e',
                              on=True,
                              label="Backup When Saving",
                              labelPosition="right",
                              style={'padding': 0,
                                     'margin': 0,
                                     'display': 'block'})
        ])
    ])
    return page_layout


@callback(
    Output('adding-rows-table-e', 'data'),
    Input('editing-rows-button-e', 'n_clicks'),
    State('adding-rows-table-e', 'data'),
    State('adding-rows-table-e', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        new_row = {}
        for c in columns:
            new_row_value = '' if c['id'] != 'Date' else datetime.datetime.today().strftime("%m/%d/%Y")
            new_row[c['id']] = new_row_value
        rows.append(new_row)
    return rows


@callback(
    Output('occultum-sum-e', 'children'),
    Input('save-button-e', 'n_clicks'),
    Input('backup-switch-e', 'on'),
    State('adding-rows-table-e', 'data'))
def save_changes(n_clicks: int, on: bool, rows: dict) -> None:
    if n_clicks > 0:
        # get dataframe back from dash table
        # write saved changes to file
        df = pd.DataFrame(rows)
        # convert revert
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        df["Date"] = df["Date"].dt.strftime("%m/%d/%Y")
        df.to_csv(file_path, index=False)

        # backup expense .csv
        if on:
            backup_file_name = f"{file_name}_{datetime.datetime.today().strftime('%Y%m%d%H%M%S')}.csv"
            backup_file_dir = os.path.join(file_dir, "backup")
            if not os.path.isdir(backup_file_dir):
                os.mkdir(backup_file_dir)
            df.to_csv(os.path.join(backup_file_dir, backup_file_name), index=False)
