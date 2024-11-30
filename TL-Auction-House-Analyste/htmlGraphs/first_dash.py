from dash import Dash, html, dash_table, dcc
import pandas as pd

# Load the data from Parquet file
df = pd.read_parquet("sales_price.parquet")

# Initialize the Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1('My First App with Data'),
    # Graph to visualize data
    dcc.Graph(
        id='my-graph',
        figure={
            'data': [
                {
                    'x': df['item_name'],  # X-axis data
                    'y': df['sale_price'],  # Y-axis data
                    'type': 'bar',  # Bar chart type
                    'name': 'Sales'
                }
            ],
            'layout': {
                'title': 'Sales Price by Item',
                'xaxis': {'title': 'Item Name'},
                'yaxis': {'title': 'Sale Price'}
            }
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
