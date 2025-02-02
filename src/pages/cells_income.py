from pathlib import Path
import dash

from dash import dash_table, html, Input, Output, State, callback
import dash_daq as daq
import datetime

import pandas as pd
import os

# register page in app
dash.register_page(__name__,
                   title='Income Data Editor',
                   name='Income Data Editor')

# Load data
data_fp = Path(__file__).parents[2] / "data"
file_path = data_fp / "Expenses - Income_Data.csv"


def layout():
    df_income = pd.read_csv(file_path, dtype={"Name": "object",
                                              "Amount": "float",
                                              "Type": "category",
                                              "Date": "object"})

    cols = df_income.columns

    page_layout = html.Div([
        dash_table.DataTable(
            id='adding-rows-table-i',
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
            data=df_income.to_dict('records'),
            dropdown={
                'Type': {
                    'clearable': False,
                    'options': [
                        {'label': i, 'value': i}
                        for i in df_income['Type'].unique()
                    ]
                }},
            editable=True,
            fill_width=False,
            row_deletable=True,
            page_size=500
        ),
        html.Div(id='occultum-sum-i', hidden=True),
        html.Div([
            html.Button('Add Row', id='editing-rows-button-i', n_clicks=0),
            html.Button('Save Changes', id='save-button-i', n_clicks=0),
            daq.BooleanSwitch(id='backup-switch-i',
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
    Output('adding-rows-table-i', 'data'),
    Input('editing-rows-button-i', 'n_clicks'),
    State('adding-rows-table-i', 'data'),
    State('adding-rows-table-i', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@callback(
    Output('occultum-sum-i', 'children'),
    Input('save-button-i', 'n_clicks'),
    Input('backup-switch-i', 'on'),
    State('adding-rows-table-i', 'data'))
def save_changes(n_clicks: int, on: bool, rows: dict) -> None:
    if n_clicks > 0:
        # get dataframe back from dash table
        # write saved changes to file
        df = pd.DataFrame(rows).sort_values("Date")
        df.to_csv(file_path, index=False)

        # backup expense .csv
        if on:
            backup_file_name = f"{file_name}_{datetime.datetime.today().strftime('%Y%m%d%H%M%S')}.csv"
            backup_file_dir = os.path.join(file_dir, "backup")
            if not os.path.isdir(backup_file_dir):
                os.mkdir(backup_file_dir)
            df.to_csv(os.path.join(backup_file_dir, backup_file_name), index=False)
