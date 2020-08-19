import dash
import dash_core_components as dcc
from pathlib import Path
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from scipy.stats import binom
import plotly.express as px
import flask

covid = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
covid_copy = covid[(covid.county !='Unknown') & (covid.state != 'Puerto Rico') & (covid.state != 'Virgin Islands')].copy()
census = pd.read_csv('https://raw.githubusercontent.com/dirtylittledirtbike/census_data/master/census_formatted3.csv')

county_state_vals = covid_copy.state + ': ' + covid_copy.county

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
                                                       {'label': 'Conservative', 'value': '5'},
                                                       {'label': 'Moderate', 'value': '10'},
                                                       {'label': 'Aggressive', 'value': '20'}
                                                       ]
                                              ),
                                 
                                 html.Div([
                                           html.P('Max Group Size:', style={"margin-top":"0%","margin-bottom": "auto"}),
                                           dcc.Input(id="group_size", type="number",value='100', style={'width':'25%'}),
                                           html.Button(id='submit-button-state', children='Submit', style={'width':'25%'}),
                                           ], style={'display':'inline'})

                                 ],
                                style={'width':'30%', 'height':'auto', 'display':'grid', 'width':'40%'}
                                ),
                       
                       html.Div(id='output-graph'),
                       
                       html.P(' ', style={"height": "auto","margin-bottom": "auto", "font-size":"35px"}),
                       
                       dcc.Markdown(
                                    ">Estimation Bias = The value we multiply the number of active cases by to account for under reporting.\n >(conservative = 5, moderate = 10, aggressive = 20).\n\n>Risk = Probability that at least one person in the group is infected 1-(1-PI)^n.\n>PI = (Number active covid cases in county × Estimation bias) / (county population).\n>n = group size.\n\n>Note: For New York City figures specify 'New York City' under Counties.",
                                    style={"white-space": "pre", "font-size":"13px"}
                                    ),
                       
                       html.P(' ', style={"height": "auto","margin-bottom": "auto", "font-size":"35px"}),

                       dcc.Markdown(
                                    "Figures updated daily, for questions contact cwestnedge@gmail.com. [Disclaimer](/get_disclaimer 'These figures are just estimates based on data that most likely does not capture the full picture. There are many unknowns due to under reporting and imperfect data that require a number of assumptions to be made in creating this model. The intent is to simply visualize our estimates and quantify risk based on the available data. This model does not claim to fully depict the actual population, but instead serves as an estimate').",
                                    style={"white-space": "pre", "font-size":"11px"}
                                    )
                       
                      ],
                      )


@app.callback(
              Output(component_id='output-graph', component_property='children'),
              [Input('submit-button-state', 'n_clicks')],
              state=[State('state_county', 'value'), State('bias', 'value'), State('group_size', 'value')]
              )

def update_graph(n_clicks, state_county, bias, group_size):
    try:
        max_group_size = int(group_size)
        region_info = [x.split(': ') for x in state_county]
        counties = []
        states = []

        for val in region_info:
            states.append(val[0])
            counties.append(val[1])

        census_df = pd.read_csv('https://raw.githubusercontent.com/dirtylittledirtbike/census_data/master/census_formatted3.csv')
        us_df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')

        def get_population(county, state):
            return census_df[(census_df.county == county)&(census_df.state == state)]['population'].values[0]

        county_population_sizes = []
        for i in range(len(states)):
            county_population_sizes.append(get_population(counties[i], states[i]))

        county_dfs = []

        for i in range(len(states)):
            temp = us_df[(us_df.state == states[i]) & (us_df.county == counties[i])].copy()
            county_dfs.append(temp)

        #    def format_date(col):
        #        split = col.split('--')
        #        return ''.join(split)
        #
        #    for county in county_dfs:
        #        county['date'] = county.date.apply(format_date)
        #        county['date'] = pd.to_datetime(county['date'], format='%Y%m%d')

        last_fourteen_days = []
        for county in county_dfs:
            last_fourteen_days.append(county.tail(14).copy())

        prob_arrs = []
        for i in range(len(states)):
            total_cases = abs(last_fourteen_days[i].iloc[-1,:].cases - last_fourteen_days[i].iloc[0,:].cases)
            # this is the line we need to change to account for under reporting for covid cases
            infected = total_cases * int(bias)
            pi = infected/county_population_sizes[i]
            group_size = range(max_group_size+1)
            prob_arrs.append((1-binom.pmf(0, group_size, pi)) * 100)

        new_dfs = []
        for i in range(len(states)):
            df = pd.DataFrame({'Risk': prob_arrs[i]})
            df['state'] = states[i]
            df['county'] = counties[i]
            new_dfs.append(df)

        risk_df = pd.concat(new_dfs)
        risk_df2 = risk_df.reset_index()
        risk_df2.columns = ['Group_Size' if x=='index' else x for x in risk_df2.columns]
        risk_df2['county'] = risk_df2.county.str.title()

        fig = px.line(risk_df2, x="Group_Size", y="Risk", \
                      color='county', width=850, height=650, title="Current Covid Risk % by Group Size")

        return dcc.Graph(id='Risk', figure=fig)
    except:
        return "Error: Unable to graph data. Please report this bug to cwestnedge@gmail.com so improvements can be made."

@app.server.route("/get_disclaimer")
def get_disclaimer():
    return flask.send_from_directory(HERE, "info.html")

if __name__ == '__main__':
    app.run_server(debug=True)
