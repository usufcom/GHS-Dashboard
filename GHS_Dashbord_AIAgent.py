import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load and preprocess the data
df = pd.read_excel('GHS1.xlsx')
df.columns = df.columns.str.strip()

# Data Cleaning
df['Year'] = pd.to_datetime(df['Year'], format='%Y').dt.year

# Calculate Key Metrics
all_diseases = df['Disease Name'].unique()

# Initialize Dash App
app = Dash(__name__)

# Custom HTML with Chatbot
app.index_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Health Statistics Dashboard</title>
    <script type="text/javascript">
        (function(d, t) {
            var v = d.createElement(t), s = d.getElementsByTagName(t)[0];
            v.onload = function() {
                if (!document.getElementById('root')) {
                    var root = d.createElement('div');
                    root.id = 'root';
                    d.body.appendChild(root);
                }
                if (window.myChatWidget && typeof window.myChatWidget.load === 'function') {
                    window.myChatWidget.load({
                        id: 'db8cbe04-26c0-407f-b11b-a961de5de970',
                    });
                }
            };
            v.src = "https://agentivehub.com/production.bundle.min.js";
            v.type = "text/javascript";
            s.parentNode.insertBefore(v, s);
        })(document, 'script');
    </script>
</head>
<body style="margin: 0; padding: 0; background-color: #121212; color: white; font-family: Arial, sans-serif;">
    <div style="padding: 20px; text-align: center;">
        <h1>Global Health Statistics Dashboard</h1>
        <p>Explore disease prevalence, healthcare insights, and more.</p>
    </div>
    <div id="dash-app">
        {%app_entry%}
    </div>
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
"""

# Layout of the Dashboard
app.layout = html.Div([
    dcc.Dropdown(
        id='disease-dropdown',
        options=[{'label': disease, 'value': disease} for disease in all_diseases],
        value=all_diseases[0],
        clearable=False,
        style={'marginBottom': '10px'}
    ),
    dcc.Graph(id='disease-map')
])

# Callback to Update the Map
@app.callback(
    Output('disease-map', 'figure'),
    Input('disease-dropdown', 'value')
)
def update_map(selected_disease):
    filtered_df = df[df['Disease Name'] == selected_disease].sort_values(by='Year')

    fig = px.choropleth(
        filtered_df,
        locations='Country',
        locationmode='country names',
        color='Prevalence Rate (%)',
        hover_name='Country',
        animation_frame='Year',
        title=f'{selected_disease} Prevalence by Country'
    )

    fig.update_layout(
        template='plotly_dark',
        geo=dict(
            bgcolor='#121212',
            showframe=False,
            showcountries=True,
            projection_type='natural earth',
            landcolor='lightgray',
            lakecolor='black'
        ),
        paper_bgcolor='#1E1E1E',
        margin=dict(l=10, r=10, t=40, b=10)
    )

    return fig

# Run the App
if __name__ == '__main__':
    app.run_server(debug=True)
