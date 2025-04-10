# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}, 
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'}, 
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                {'label': 'All Sites', 'value': 'ALL'}
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True
        )
    ]),
    
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    html.Div([
        dcc.RangeSlider(
            id='payload-slider',
            min=min_payload,
            max=max_payload,
            step=1000,
            marks={i: f'{i}' for i in range(0, int(max_payload) + 1, 2500)},
            value=[min_payload, max_payload]
        )
    ]),
    
    html.Br(),
    
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # Filter the dataframe based on the selected launch site
    if entered_site == 'ALL':
        # Pie chart for all launch sites
        fig = px.pie(
            spacex_df, 
            values='class',  # 'class' contains the success/failure (1/0) data
            names='Launch Site',  # Group by launch site
            title='Total Success Launches by Site'
        )
        return fig
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Create a pie chart showing success (class=1) and failure (class=0) for the selected site
        # Convert numeric class values to string labels for better readability
        filtered_df['outcome'] = filtered_df['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            filtered_df, 
            names='outcome',  # Group by success/failure
            title=f'Success vs Failure for Site {entered_site}',
            hole=0.3,  # To make it a donut chart, optional
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter by payload mass range
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    # Filter by launch site if a specific site was selected
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class',
        color='Booster Version Category',
        title=f'Correlation between Payload and Success for {entered_site if entered_site != "ALL" else "All Sites"}',
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)