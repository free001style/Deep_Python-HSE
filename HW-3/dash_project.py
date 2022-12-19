from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

app = Dash(__name__)
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = pd.read_csv("crimedata.csv")
code_cols = ['countyCode', 'communityCode']
for col in code_cols:
    df[col] = df[col].fillna(value=0)
    df[col] = df[col].astype('int')
suffixes = ['township', 'city', 'borough']
for suffix in suffixes:
    df['communityName'] = df['communityName'].str.replace(suffix, '')

states = list(df.state.unique())
races = {'Black': 'racepctblack', 'White': 'racePctWhite', 'Asian': 'racePctAsian', 'Spanish': 'racePctHisp'}
crimes = dict(zip(['murdPerPop', 'rapesPerPop', 'robbbPerPop',
                   'assaultPerPop', 'burglPerPop', 'larcPerPop',
                   'autoTheftPerPop', 'arsonsPerPop', 'ViolentCrimesPerPop',
                   'nonViolPerPop'],
                  ['murders', 'rapes', 'robberies', 'assaults', 'burglaries', 'larcenies', 'autoTheft', 'arsons',
                   'ViolentCrimes', 'nonViolentCrimes']))

app.layout = html.Div([
    html.Div([html.H3('Salaries and poor people by state'),
              dcc.Checklist(id="checklist_for_states1", options=states, value=states, inline=True),
              dcc.Graph(id='sal_poor'),
              html.P("Subplots Width:"),
              dcc.Slider(
                  id='slider-width', min=.1, max=.9,
                  value=0.5, step=0.1)]),
    html.Div([html.H3('Immigration and race percentage in each state'),
              dcc.Dropdown(
                  id="dropdown",
                  options={"PctImmigRecent": 'Percentage of immigrants who immigated within last 3 years',
                           "PctImmigRec5": 'Percentage of immigrants who immigated within last 5 years',
                           "PctImmigRec8": 'Percentage of immigrants who immigated within last 8 years',
                           "PctImmigRec10": 'Percentage of immigrants who immigated within last 10 years'},
                  value="PctImmigRec10",
                  clearable=False,
              ), dcc.Checklist(id="checklist_for_states2", options=states, value=states, inline=True),
              dcc.RadioItems(["White", "Black", "Asian", "Spanish"], "Black", id='radio', inline=True),
              dcc.Graph(id="graph")]),
    html.Div([html.H3('Total number of crime types per 100K population in each state'),
              dcc.Dropdown(id='dropdown_for_type_crimes', options=crimes, value='murdPerPop', clearable=False),
              dcc.Checklist(id="checklist_for_states3", options=states, value=states, inline=True),
              dcc.Graph(id='graph_for_type_crimes')]),
    html.Div([html.H3('Police officers per 100K population'),
              dcc.Checklist(id="checklist_for_states4",
                            options=states, value=states,
                            inline=True),
              dcc.Graph(id="police_per_100k")]),
    html.Dfn(
        [html.H3('Percent of occupied housing units without phone and complete plumbing facilities'),
         dcc.Graph(id="plumb_phone"),
         dcc.Checklist(id="checklist_for_states5", options=states, value=states, inline=True)])
])


@app.callback(Output("sal_poor", "figure"),
              Input("checklist_for_states1", "value"),
              Input("slider-width", "value"))
def sal_poor(state, left_width):
    df1 = df.groupby('state')['medIncome'].mean().reset_index().sort_values('medIncome')
    df2 = df.groupby('state')['PctPopUnderPov'].mean().reset_index().sort_values('PctPopUnderPov', ascending=False)
    df1 = df1[df1.state.isin(state)]
    df2 = df2[df2.state.isin(state)]

    fig = make_subplots(rows=1, cols=2, column_widths=[left_width, 1 - left_width],
                        subplot_titles=('Median household income', 'Percentage of people under the poverty level'))
    fig.add_trace(row=1, col=1, trace=go.Bar(x=df1['state'], y=df1['medIncome'], name='Salary'))
    fig.add_trace(row=1, col=2, trace=go.Bar(x=df2['state'], y=df2['PctPopUnderPov'], name='Poor'))
    fig.update_xaxes(row=1, col=1, tickfont={'size': 8}, patch={'tickangle': -45})
    fig.update_xaxes(row=1, col=2, tickfont={'size': 8}, patch={'tickangle': -45})
    return fig


@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value"),
    Input("checklist_for_states2", "value"),
    Input("radio", 'value'))
def update_bar_chart(imm, state, race):
    fig = go.Figure()
    df1 = df.groupby('state')[races[race]].mean().reset_index()
    df2 = df.groupby('state')[imm].mean().reset_index()
    df1 = df1[df1.state.isin(state)]
    df2 = df2[df2.state.isin(state)]
    fig.add_trace(go.Bar(x=df1['state'], y=df1[races[race]], name='race', marker_color='indianred'))
    fig.add_trace(go.Bar(x=df1['state'], y=df2[imm], name='immigration percent', marker_color='lightsalmon'))
    fig.update_xaxes(patch={'tickangle': -45})
    return fig


@app.callback(Output('graph_for_type_crimes', 'figure'), Input("checklist_for_states3", "value"),
              Input('dropdown_for_type_crimes', 'value'))
def graph_for_type_crimes(state, type):
    df1 = df.groupby('state')[type].mean().reset_index()
    df1 = df1[df1.state.isin(state)]
    fig = px.bar(df1, x='state', y=type)
    fig.update_yaxes(title_text=crimes[type])
    return fig


@app.callback(Output('police_per_100k', 'figure'), Input('checklist_for_states4', 'value'))
def police_per_100k(state):
    df1 = df.groupby('state')['PolicPerPop'].mean().reset_index()
    df1 = df1[df1.state.isin(state)]
    fig = px.bar(df1, x='state', y='PolicPerPop',
                 color_discrete_sequence=["magenta"])
    return fig


@app.callback(
    Output("plumb_phone", "figure"),
    Input("checklist_for_states5", 'value'))
def update_bar_chart(state):
    fig = go.Figure()
    df1 = df.groupby('state')['PctHousNoPhone'].mean().reset_index()
    df2 = df.groupby('state')['PctWOFullPlumb'].mean().reset_index()
    df1 = df1[df1.state.isin(state)]
    df2 = df2[df2.state.isin(state)]
    fig.add_trace(go.Bar(x=df1['state'], y=df1['PctHousNoPhone'], name='w/o phone', marker_color='indianred'))
    fig.add_trace(
        go.Bar(x=df1['state'], y=df2['PctWOFullPlumb'], name='w/o plumbing facilities', marker_color='lightsalmon'))
    fig.update_xaxes(patch={'tickangle': -45})
    return fig


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=4444, debug=True)
