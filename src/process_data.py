import pandas as pd
from scipy.stats import binom

def get_risk(df1, df2, locations_list, bias, max_group_size):
    census_df = df1
    us_df = df2
    
    def get_population(loc):
        return census_df[census_df.Location == loc]['population'].values[0]
    
    county_population_sizes = []
    
    for loc in locations_list:
        county_population_sizes.append(get_population(loc))
    
    county_dfs = []

    for loc in locations_list:
        temp = us_df[us_df.Location == loc].copy()
        county_dfs.append(temp)
    
    last_fourteen_days = []
    for county in county_dfs:
        last_fourteen_days.append(county.tail(14).copy())
    
    prob_arrs = []
    for i in range(len(locations_list)):
        total_cases = abs(last_fourteen_days[i].iloc[-1,:].cases - last_fourteen_days[i].iloc[0,:].cases)
        # this is the line we need to change to account for under reporting for covid cases
        infected = total_cases * bias
        pi = infected/county_population_sizes[i]
        group_size = range(max_group_size+1)
        prob_arrs.append((1-binom.pmf(0, group_size, pi)) * 100)
    
    new_dfs = []
    for i in range(len(locations_list)):
        df = pd.DataFrame({'Risk': prob_arrs[i]})
        df['Location'] = locations_list[i]
        new_dfs.append(df)

    risk_df = pd.concat(new_dfs)
    risk_df2 = risk_df.reset_index()
    risk_df2.columns = ['Group Size' if x=='index' else x for x in risk_df2.columns]

    return risk_df2


if __name__ == '__main__':
    from plotly import express as px
    
    covid_df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
    covid_df = covid_df[(covid_df.county !='Unknown')\
                        & (covid_df.state != 'Puerto Rico')\
                        & (covid_df.state != 'Virgin Islands')].copy()
                        
    census_df = pd.read_csv('https://raw.githubusercontent.com/dirtylittledirtbike/census_data/master/census_formatted3.csv')
    
    covid_df['Location'] = covid_df.state + ': ' + covid_df.county
    census_df['Location'] = census_df.state + ': ' + census_df.county

    locations_list = ['Illinois: Cook', 'Texas: Harris', 'Louisiana: Orleans', 'Texas: Travis']
    estimation_bias = int(10)
    max_group_size = 100

    risk_df = get_risk(census_df, covid_df, locations_list, estimation_bias, max_group_size)

    fig2 = px.line(risk_df, x="Group Size", y="Risk",\
                   color='Location', width=800, height=700, title="Current Covid Risk % by Group Size")

    fig2.show()
