import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load and preprocess the data
df = pd.read_excel('GHS1.xlsx')
#df = pd.read_csv('GHS2.csv')
df.columns = df.columns.str.strip()

# Data Cleaning
df['Year'] = pd.to_datetime(df['Year'], format='%Y').dt.year

# Calculate Key Metrics
top_diseases = df.groupby('Disease Name')['Mortality Rate (%)'].mean().nlargest(10).reset_index()
mortality_trend = df.groupby(['Year'])['Mortality Rate (%)'].mean().reset_index()
healthcare_access = df.groupby('Country')['Healthcare Access (%)'].mean().reset_index()

# Filter Data for Relevant Diseases and Countries
selected_diseases = ['Malaria', 'HIV/AIDS', 'Respiratory Infections', 'Tuberculosis', 'Diabetes']
filtered_disease_df = df[df['Disease Name'].isin(selected_diseases)]

selected_countries = ['United States', 'Nigeria', 'Brazil', 'India', 'Germany', 'Australia']
filtered_country_df = df[df['Country'].isin(selected_countries)]

# Get all unique diseases for dropdown
all_diseases = df['Disease Name'].unique()

# Initialize Dash App
app = Dash(__name__)

# Layout of the Dashboard
app.layout = html.Div([
    html.Div([
        html.H1("Global Health Statistics Dashboard",
                style={'textAlign': 'center', 'color': 'white', 'padding': '10px'}),
        html.H4("Comprehensive Health Insights by Disease and Country. Explore disease prevalence, healthcare insights, and more.",
                style={'textAlign': 'center', 'color': '#AAAAAA', 'fontStyle': 'italic'}),
        html.H4("Designed by Youssoufa M.",
                style={'textAlign': 'center', 'color': '#AAAAAA', 'fontStyle': 'italic'}),
    ], style={'backgroundColor': '#1E1E1E', 'padding': '20px'}),

    # Dropdown for Disease Selection
    html.Div([
        html.Label("Select Disease", style={'color': 'white'}),
        dcc.Dropdown(
            id='disease-dropdown',
            options=[{'label': disease, 'value': disease} for disease in all_diseases],
            value=all_diseases[0],  # Default value to the first disease
            clearable=False,
            style={
                'backgroundColor': '#AAAAAA',
                'color': 'black'  # Dark dropdown text
            }
        )
    ], style={'padding': '20px'}),

    # Disease Prevalence Map
    html.Div([
        dcc.Graph(id='disease-map')
    ], style={'padding': '20px', 'height': '800px'}),  # Increase map container height

    # Top 10 Diseases by Mortality
    html.Div([
        dcc.Graph(
            id='top-diseases',
            figure=px.bar(
                filtered_disease_df,
                x='Mortality Rate (%)',
                y='Disease Name',
                orientation='h',
                title='Diseases by Mortality Rate'
            ).update_layout(
                template='plotly_dark',
                plot_bgcolor='#1E2B45',
                paper_bgcolor='#1E2B45'
            )
        )
    ], style={'padding': '20px'}),

    # Mortality Rate Trend
    html.Div([
        dcc.Graph(
            id='mortality-trend',
            figure=px.line(
                mortality_trend,
                x='Year',
                y='Mortality Rate (%)',
                title='Mortality Rate Trends Over Time',
                markers=True
            ).update_layout(
                template='plotly_dark',
                plot_bgcolor='#2E2E2E',
                paper_bgcolor='#2E2E2E'
            )
        )
    ], style={'padding': '20px'}),

    # Healthcare Access by Country
    html.Div([
        dcc.Graph(
            id='healthcare-access',
            figure=px.bar(
                healthcare_access,
                x='Country',
                y='Healthcare Access (%)',
                title='Healthcare Access by Country'
            ).update_layout(
                template='plotly_dark',
                plot_bgcolor='#354B29',
                paper_bgcolor='#354B29'
            )
        )
    ], style={'padding': '20px'}),

    # Recovery Rate vs Treatment Cost (Selected Diseases)
    html.Div([
        dcc.Graph(
            id='recovery-vs-cost',
            figure=px.scatter(
                filtered_disease_df,
                x='Average Treatment Cost (USD)',
                y='Recovery Rate (%)',
                color='Disease Name',
                size='Population Affected',
                hover_name='Country',
                title='Recovery Rate vs Treatment Cost (Top 5 Diseases)'
            ).update_layout(
                template='plotly_dark',
                plot_bgcolor='#1E1E1E',
                paper_bgcolor='#1E1E1E',
                height=500
            )
        )
    ], style={'padding': '20px'}),

    # Education Index vs Healthcare Access (Selected Countries)
    html.Div([
        dcc.Graph(
            id='education-health-access',
            figure=px.scatter(
                filtered_country_df,
                x='Education Index',
                y='Healthcare Access (%)',
                color='Country',
                size='Doctors per 1000',
                hover_name='Country',
                title='Education Index vs Healthcare Access (Selected Countries)'
            ).update_layout(
                template='plotly_dark',
                plot_bgcolor='#1E1E1E',
                paper_bgcolor='#1E1E1E',
                height=500
            )
        )
    ], style={'padding': '20px'}),

    # Incidence Rate by Disease (Selected Countries)
    html.Div([
        dcc.Graph(
            id='incidence-rate',
            figure=px.bar(
                filtered_country_df,
                x='Country',
                y='Incidence Rate (%)',
                color='Disease Name',
                barmode='group',
                hover_name='Country',
                title='Incidence Rate of Diseases in Selected Countries'
            ).update_layout(
                template='plotly_dark',
                plot_bgcolor='#1E1E1E',
                paper_bgcolor='#1E1E1E',
                height=500
            )
        )
    ], style={'padding': '20px'})

], style={'backgroundColor': '#121212', 'padding': '30px'})


# Callback to update the map based on dropdown selection
@app.callback(
    Output('disease-map', 'figure'),
    Input('disease-dropdown', 'value')
)
def update_map(selected_disease):
    # Filter the data for the selected disease
    filtered_df = df[df['Disease Name'] == selected_disease].sort_values(by='Year')

    # Create the choropleth map
    fig = px.choropleth(
        filtered_df,
        locations='Country',
        locationmode='country names',
        color='Prevalence Rate (%)',
        hover_name='Country',
        animation_frame='Year',
        title=f'{selected_disease} Prevalence by Country'
    )

    # Update layout for better visualization
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
        margin=dict(l=10, r=10, t=40, b=10),
        height=700
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
