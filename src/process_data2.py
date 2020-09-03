import pandas as pd

def get_time_series(df, location_list, estimation_bias):
    df2 = df[df.Date > '2020-03-16'].copy()
	
    dfs = [df2[df2.Location == item].copy() for item in location_list]
	
    for data in dfs:
        data['daily_increase'] = abs(data.cases.diff())
        data['New Cases'] = data.daily_increase.rolling(7).mean()
	
    return pd.concat(dfs)


if __name__ == '__main__':
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    location_list = ['Illinois: Cook', 'Texas: Harris', 'Louisiana: Orleans', 'Texas: Travis']
    estimation_bias = 10

    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
    df['Location'] = df.state + ': ' + df.county
    df['Date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
    new_df = get_time_series(df, location_list, estimation_bias)



    fig = make_subplots(rows=len(location_list),
                        cols=1,
                        subplot_titles=location_list,
                        shared_yaxes=False,
                        vertical_spacing=0.075)

    for i, loc in enumerate(location_list):
        
        fig.append_trace(go.Scatter(customdata=new_df[new_df.Location==loc]['daily_increase'],
                                    hovertemplate="%{x}<br><br>7-Day Rolling Mean: %{y}<br>New Cases: %{customdata}<extra></extra>",
                                    x=new_df[new_df.Location == loc].Date,
                                    y=new_df[new_df.Location == loc]['New Cases'],
                                    ), row=i+1, col=1)
                                    
        fig.append_trace(go.Bar(hoverinfo='none',
                                x=new_df[new_df.Location == loc].Date,
                                y=new_df[new_df.Location == loc]['daily_increase']
                                ),row=i+1, col=1)

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=11)

    fig.update_layout(height=700,
                      width=500,
                      title_text="Newly Confirmed Cases",
                      font_family="Times New Roman",
                      showlegend=False)

    fig.show()
    
#    plt = go.Figure()
#    plt.add_trace(go.Bar(x=new_df.Date, y=new_df.daily_increase))
#    plt.show()

#    fig = px.line(new_df, x='Date',
#              y='New Cases',
#              width=700,
#              height=600,
#              facet_col='Location',
#              facet_col_wrap=1,
#              color='Location',
#              title='Confirmed Cases (7 day rolling mean)')

              
              
#    fig.add_bar(x=new_df[new_df.Location == 'Texas: Travis'].Date,\
#                y=new_df[new_df.Location == 'Texas: Travis'].daily_increase,\
#                name="idk", facet_col='Location', facet_col_wrap=1)

#    import plotly.graph_objects as go
#    data = []
#    for loc in location_list:
#        data.append(go.Bar(
#                           x = new_df[new_df.Location == loc].Date,
#                           y = new_df[new_df.Location == loc].daily_increase,
#                           ))
#        data.append(
#                    go.Scatter(
#                               x = new_df[new_df.Location == loc].Date,
#                               y = new_df[new_df.Location == loc]['New Cases'],
#                               )
#                    )
#
#    plot = go.Figure(data)
#
#    plot.show()
#
#    fig.update_yaxes(matches=None)
#    fig.show()
