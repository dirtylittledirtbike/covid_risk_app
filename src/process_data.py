import pandas as pd
from scipy.stats import binom

def get_risk(df1, df2, states, counties, bias, max_group_size):
    census_df = df1
    us_df = df2

    def get_population(county, state):
        return census_df[(census_df.county == county)&(census_df.state == state)]['population'].values[0]
    
    county_population_sizes = []
    for i in range(len(states)):
        county_population_sizes.append(get_population(counties[i], states[i]))

    county_dfs = []

    for i in range(len(states)):
        temp = us_df[(us_df.state == states[i]) & (us_df.county == counties[i])].copy()
        county_dfs.append(temp)

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
        df['State/County'] = states[i] + '-' + counties[i]
        new_dfs.append(df)
    
    risk_df = pd.concat(new_dfs)
    risk_df2 = risk_df.reset_index()
    risk_df2.columns = ['Group_Size' if x=='index' else x for x in risk_df2.columns]

    return risk_df2
