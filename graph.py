import dash
import dash_core_components as dcc
from pathlib import Path
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from src.process_data import get_risk
from src.process_data2 import get_time_series
import plotly.express as px
import flask
import plotly

print(plotly.__version__)
# --- preprocessing ---
covid_df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
covid_df = covid_df[(covid_df.county !='Unknown') & (covid_df.state != 'Puerto Rico') & (covid_df.state != 'Virgin Islands')].copy()
census_df = pd.read_csv('https://raw.githubusercontent.com/dirtylittledirtbike/census_data/master/census_formatted3.csv')
county_state_vals = covid_df.state + ': ' + covid_df.county
covid_df['date'] = pd.to_datetime(covid_df.date, format='%Y-%m-%d')

covid_df['location'] = covid_df.state + ': ' + covid_df.county
census_df['location'] = census_df.state + ': ' + census_df.county
# --- preprocessing ---

HERE = Path(__file__).parent
app = dash.Dash()
app.title = '🎠'
app.layout = html.Div(
                      [
                       html.Div([
                                 html.Label('State/County: '),
                                 dcc.Dropdown(id='state_county', value=['Texas: Harris', 'Illinois: Cook'],
                                              options=[{'label': k, 'value': k} for k in county_state_vals.sort_values(ascending=True).unique()],
                                              multi=True
                                              ),

                                 
                                 html.Label('Estimation Bias:'),
                                 dcc.Dropdown(id='bias', value='10',
                                              options=[
                                                       {'label': 'None', 'value': '1'},
                                                       {'label': 'Conservative', 'value': '5'},
                                                       {'label': 'Moderate', 'value': '10'},
                                                       {'label': 'Aggressive', 'value': '20'}
                                                       ]
                                              ),
                                 
                                 html.Div([
                                           html.P('Max Group Size:', style={"marginTop":"0%","marginBottom": "auto"}),
                                           dcc.Input(id="group_size", type="number",value='100', style={'width':'25%'}),
                                           html.Button(id='submit-button-state', children='Submit', style={'width':'25%'}),
                                           ], style={'display':'inline'})

                                 ],
                                style={'width':'30%', 'height':'auto', 'display':'grid', 'width':'40%'}
                                ),
                       
                       html.Div(id='output-graph', style = {'display':'flex'} ),
#                       html.Div(id='output-graph', style = {'columnCount': 2, 'height':'auto', 'width':'auto'}),
#                       html.Div(id='output-graph2'),
                       
#                       html.P(' ', style={"height": "auto","marginBottom": "auto", "fontSize":"35px"}),
                       
                       dcc.Markdown(
                                    ">Estimation Bias = The value we multiply the number of active cases by to account for under reporting.\n >(None= 1, conservative = 5, moderate = 10, aggressive = 20).\n\n>Risk = Probability that at least one person in the group is infected 1-(1-PI)^n.\n>PI = (Number active covid cases in county × Estimation bias) / (county population).\n>n = group size.\n\n>Note: For New York City figures specify 'New York City' under Counties.",
                                    style={"whiteSpace": "pre", "fontSize":"13px"}
                                    ),
                       
                       html.P(' ', style={"height": "auto","marginBottom": "auto", "fontSize":"35px"}),

                       dcc.Markdown(
                                    "Figures updated daily, for questions contact cwestnedge@gmail.com. [Disclaimer](/get_disclaimer 'These figures are just estimates based on data that most likely does not capture the full picture. There are many unknowns due to under reporting and imperfect data that require a number of assumptions to be made in creating this model. The intent is to simply visualize our estimates and quantify risk based on the available data. This model does not claim to fully depict the actual population, but instead serves as an estimate').",
                                    style={"whiteSpace": "pre", "fontSize":"11px"}
                                    ),
                       
                       # hidden div
#                       html.Div(id='intermediate-value', style={'display': 'none'})
                       
                      ],
                      )

@app.callback(
              Output(component_id='output-graph', component_property='children'),
              [Input('submit-button-state', 'n_clicks')],
              state=[State('state_county', 'value'), State('bias', 'value'), State('group_size', 'value')]
              )
def update_graph(n_clicks, state_county, bias, group_size):
#    try:
    max_group_size = int(group_size)
    risk_df = get_risk(census_df, covid_df, state_county, int(bias), max_group_size)
    time_series_df = get_time_series(covid_df, state_county, int(bias))
    
    fig = px.line(risk_df,
                  x="Group_Size",
                  y="Risk",
                  color='location',
                  width=700,
                  height=600,
                  title="Current Covid Risk % by Group Size")
                  
    fig.update_layout(
                      legend=dict(
                                  x=0,
                                  y=1,
                                  traceorder="reversed",
                                  title_font_family="Times New Roman",
                                  font=dict(
                                            family="Courier",
                                            size=9,
                                            color="black"
                                            ),
                                  bgcolor="LightSteelBlue",
#                                  bordercolor="Black",
#                                  borderwidth=2
                                  )
                     )

#    fig.update_traces(marker=dict(size=9,
#                                  line=dict(width=1,
#                                            color='DarkSlateGrey')),
#                      selector=dict(mode='markers'))

    fig2 = px.line(time_series_df, x="date",
                   y="new cases",
                   width=500,
                   height=700,
                   facet_col="location",
                   facet_col_wrap=1,
                   color='location')

#    fig2.update_layout(
#                       legend=dict(
#                                   x=0,
#                                   y=1,
#                                   traceorder="reversed",
#                                   title_font_family="Times New Roman",
#                                   font=dict(
#                                             family="Courier",
#                                             size=10,
#                                             color="black"
#                                             ),
#                                   bgcolor="LightSteelBlue",
#                                   )
#                      )
    fig2.update_yaxes(matches=None)
    fig2.update_layout(showlegend=False)
#    fig.show()


    return dcc.Graph(id='Risk', figure=fig), dcc.Graph(id='idk', figure=fig2)
#    except:
#        return "Error: Unable to graph data. Please select a valid State/County"

@app.server.route("/get_disclaimer")
def get_disclaimer():
    return flask.send_from_directory(HERE, "info.html")

if __name__ == '__main__':
    app.run_server(debug=True)
