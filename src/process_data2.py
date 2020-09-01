import pandas as pd

def get_time_series(df, location_list, estimation_bias):
    df2 = df[df.date > '2020-03-16'].copy()
	
    dfs = [df2[df2.location == item].copy() for item in location_list]
	
    for data in dfs:
        data['daily_increase'] = abs(data.cases.diff())
        data['new cases'] = data.daily_increase.rolling(7).mean()
	
    return pd.concat(dfs)


if __name__ == '__main__':
    import plotly.express as px

    location_list = ['Illinois: Cook', 'Texas: Harris', 'Louisiana: Orleans', 'Texas: Travis']
    estimation_bias = 10

    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
    df['location'] = df.state + ': ' + df.county
    new_df = get_time_series(df, location_list, estimation_bias)

    fig = px.line(new_df, x="date",
              y="new cases",
              width=700,
              height=600,
              facet_col="location",
              facet_col_wrap=1,
              color='location')

    fig.update_yaxes(matches=None)
    fig.show()
