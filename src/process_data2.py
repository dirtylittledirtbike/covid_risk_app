import pandas as pd

def get_time_series(df, regions, estimation_bias):
	df['state_county'] = df.state + ': ' + df.county
	df['date'] = pd.to_datetime(df.date)
	df2 = df[df.date > '2020-03-16'].copy()
	
	dfs = [df2[df2.state_county == item].copy() for item in regions]
	
	for data in dfs:
		data['daily_increase'] = abs(data.cases.diff() * estimation_bias)
		data['new cases'] = data.daily_increase.rolling(7).mean()
	
	return pd.concat(dfs)


if __name__ == '__main__':
	import plotly.express as px

	regions = regions = ['Illinois: Cook', 'Texas: Harris', 'Louisiana: Orleans', 'Texas: Travis']
	estimation_bias = 10

	df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
	new_df = get_time_series(df, regions, estimation_bias)

	fig = px.line(new_df, x="date",
              y="new cases",
              width=700,
              height=600,
              facet_col="state_county",
              facet_col_wrap=1,
              color='state_county')

	fig.update_yaxes(matches=None)
	fig.show()
