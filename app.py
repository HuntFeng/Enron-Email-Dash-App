import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
#from graph_tool.all import *
import numpy as np
from sklearn import preprocessing
from textwrap import dedent
import flask
import os
import os.path as op
import base64

le = preprocessing.LabelEncoder()


base_path = os.getcwd()
le.classes_ = np.load(op.join(base_path, "le_classes.npy"))
g = load_graph(op.join(base_path, "enron_emails_graph.xml.gz"))
df = pd.read_pickle(op.join(base_path, "enron_emails_dataframe.pickle"))

# loading local images
file1 = op.abspath("enron_network_pagerank.png") # replace with your own image
image1 = base64.b64encode(open(file1, 'rb').read()) #use base 64 to encode the image
file2 = op.abspath("enron_network_betweenness.png") # replace with your own image
image2 = base64.b64encode(open(file2, 'rb').read()) #use base 64 to encode the image

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheet=external_stylesheet)


app.layout = html.Div([
    html.H1("Enron Emails Communication Network Analysis"),
    html.P("What emails do you want to see during this analysis?"),
    dcc.RadioItems(
                id='first-filter',
                options=[{'label': "Enron-emails only", 'value': "enron"},  {'label': "All emails", 'value': "all"} ],
                value='enron',
                labelStyle={'display': 'inline-block'}
    ),

    # tabs to separate contents
    dcc.Tabs(id="tabs", value='tab-1', children=[
        # Here is Tab 1
        dcc.Tab(label='Centrality Analysis', value='tab-1', children=[
            html.H1("Centrality Analysis"),
            dcc.Dropdown(
                id='person',
                options=[ 
                    {'label': email, 'value': email } for email in df['from'].unique()
                ],
                value="billy.lemmons@enron.com"
            ),

        dcc.Markdown(id='centrality-description'),

        dcc.Markdown(dedent('''
        # Interesting people in this network
        ## Clustering
        ### average local clustering
        coef=0.18986837631369474, std=0.002117118119820023

        ### global clustering
        coef=0.11028393970879012, std=0.007023260776700652)
        ''')),

        dcc.Markdown(dedent('''
        ## Centrality
        ### pageRank
        * jeff.skilling@enron.com: 0.000904593820450777
        * kenneth.lay@enron.com: 0.0008326695951430636
        * louise.kitchen@enron.com: 0.0008237324643966968
        * tana.jones@enron.com: 0.0008008890893152812
        * sara.shackleton@enron.com: 0.0007329510657980459
        ''')),
        
        html.Img(src="data:image/png;base64,{}".format(image1.decode()) ),

        dcc.Markdown(dedent('''
        ### betweenness
        #### vetices
        * sally.beck@enron.com: 0.008996282033653259
        * kenneth.lay@enron.com: 0.007940415535286651
        * jeff.skilling@enron.com: 0.00673580231406722
        * outlook.team@enron.com: 0.006175735614700912
        * vince.kaminski@enron.com: 0.00487832471810958

        #### edges
        * andy.zipper@enron.com->bob.ambrocik@enron.com: 0.0007541178397434986
        * rod.hayslett@enron.com->tracey.kozadinos@enron.com: 0.0006790340898782624
        * outlook.team@enron.com->lee.wright@enron.com: 0.0006742490070680812
        * tana.jones@enron.com->enron.announcements@enron.com: 0.0005940634052792041
        * gerald.nemec@enron.com->louis.allen@enron.com: 0.0005010359543983454
        ''')),
        
        html.Img(src="data:image/png;base64,{}".format(image2.decode()) ),

        ] ),


        # Here is Tab 2
        dcc.Tab(label='Email Content and Sentiment', value='tab-2', children=[
            html.H1("Email Content and Sentiment"),
            #dropdown list
            html.Label('From'),
            dcc.Dropdown(
                id='sender',
                style={'position':'relative', 'zIndex':'1000'}, # place this dropdown list to the front so that the table header and the next dropdown list won't overlaps it
                options=[ 
                    {'label': email, 'value': email } for email in df['from'].unique()
                ],
                value="billy.lemmons@enron.com"
            ),

            html.Label('To'),
            dcc.Dropdown(
                id='receiver',
                style={'position':'relative', 'zIndex':'500'}, # place this dropdown list to the front so that the table header won't overlaps it
                options=[ 
                    {'label': email, 'value': email } for email in list(set(np.concatenate(df['to'].tolist())))
                ],
                value="jeff.skilling@enron.com"
            ),

            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns if (i=='date' or i=='sentavg' or i=='subject')],
                # enable multiple lines in a cell
                css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                }], 
                # display fix rows with a vertical scroll
                n_fixed_rows=1,
                # horizontal scroll
                style_table={'overflowX': 'scroll'},
                style_header={
                    'fontWeight': 'bold',
                },
            ),

            cyto.Cytoscape(
                id='cytoscape-two-nodes',
                elements=[
                    {'data': {'id': 'one', 'label': 'Node 1'}},
                    {'data': {'id': 'two', 'label': 'Node 2'}},

                    {'data': {'source': 'one', 'target': 'two', 'label': 'Edge'}}
                ],
                stylesheet=[
                    {
                        'selector': 'node',
                        'style': {
                            'label': 'data(label)'
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'label': 'data(label)',
                            'curve-style': 'bezier'
                        }
                    }
                ],
                style={'width': '80%', 'height': '500px', 'border': 'solid'},
                layout={'name': 'random'},
            ),

            html.P(id='cytoscape-display-selection')

        ]),
    ]),
    html.Div(id='tabs-content'),


])


@app.callback(
    Output('centrality-description', 'children'),
    [Input('person', 'value')])
def centrality_description(email):
    vertex_id = le.transform([email])
    v = g.vertex(vertex_id)
    return dedent('''
            * out degree = {0}
            * in degree = {1}'''.format(v.out_degree(), v.in_degree()) 
            )

@app.callback(
    Output('table', 'data'),
    [Input('sender', 'value'),
    Input('receiver', 'value')] )
def update_table(frm, to):
    nwdf = df[df['from'].str.contains(frm) & df['to'].apply(lambda x: to in x)]
    return nwdf.to_dict('records')

@app.callback(
    Output('cytoscape-two-nodes', 'elements'),
    [Input('sender', 'value'),
    Input('receiver', 'value'),
    Input('table', 'data') ] )
def update_graph(frm, to, email_list):  
    nodes = [
        {'data': {'id': 'one', 'label': frm}},
        {'data': {'id': 'two', 'label': to}}
    ]
    edge_labels = set(email_list[i]['subject'] for i in range(len(email_list)))
    edges = [ {'data': {'source': 'one', 'target': 'two', 'label': edge_label }} for edge_label in list(edge_labels) ]
    return nodes + edges

@app.callback(
    Output('cytoscape-display-selection', 'children'),
    [Input('cytoscape-two-nodes', 'selectedEdgeData'),
    Input('table', 'data')])
def show_sentiment(edges, email_list):
    if(edges):
        n = len(email_list)
        selectedEdges = []
        for edge in edges:
            label = edge['label']
            for i in range(n):
                if email_list[i]['subject'] == label:
                    sentiment = email_list[i]['sentavg']
                    break
            selectedEdges.append( label + ": " + str(sentiment) )
        return "The average sentiment the email with the title:\n" + "\n*".join(selectedEdges)

if __name__ == '__main__':
    app.run_server(debug=True)