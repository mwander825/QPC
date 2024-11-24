from dash import Dash, html, dcc
import dash

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1('Quantam Pecuniam Coacervatito?', id='title'),

    html.Div(html.A("Bottom", href="#bottom")),
    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ],

    ),
    dash.page_container,
    html.Div(html.A("Top", href="#")),
    html.Footer(id='bottom')
])

if __name__ == '__main__':
    app.run_server(debug=True)
