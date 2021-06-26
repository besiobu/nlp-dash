import collections
import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from flask_caching import Cache
from google.cloud import language_v1
from pymongo import MongoClient
import random

if ('MONGO_CREDENTIALS' in os.environ.keys() and 
    'GOOGLE_APPLICATION_CREDENTIALS' in os.environ.keys()):
    print('Using environment credentials.')
else:
    print('No credentials, using local.')
    from creds import set_credentials
    set_credentials()

timeout = 7 * 24 * 60 * 60 # Cache results for one week
color_red = 'rgb(255,152,150,0.4)'
color_green = 'rgb(152,223,138,0.4)'
color_gray = 'rgb(134,142,150,0.4)'
sentiment_threshold = 0.2

client = language_v1.LanguageServiceClient()

meta_tags = {
    'name': 'viewport', 
    'content': 'width=device-width, initial-scale=1'
}

app = dash.Dash(
    name=__name__, 
    external_stylesheets=[dbc.themes.COSMO], 
    meta_tags=[meta_tags]
)

server = app.server

app.title = 'nlp-mvp'

cache = Cache(
    app.server, 
    config={
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': '.cache'
    }
)

chart_entity = dcc.Graph(
    id='chart-entity',
    config={'displayModeBar': False},
    animate=False
)

chart_category = dcc.Graph(
    id='chart-category',  
    config={'displayModeBar': False},
    animate=False
)

style = {
    'margin': '5px 0px 10px 0px', 
    'padding': '0px'
}

app.layout = html.Div(
    children=[
        dbc.Row(
            children=dbc.Col(
                children=html.Div(
                    children=dbc.Button(
                        children='Next random article', 
                        id='button-next', 
                        outline=True, 
                        color='secondary'
                    ), 
                    style=style
                )
            ),
            style=style,
        ),        
        dbc.Row(
            children=[
                dbc.Col(
                    children=html.Div(
                        children=dbc.Card(
                            children=[
                                dbc.CardHeader(
                                    children=html.H4('Title'), 
                                    className='card-title'
                                ), 
                                dbc.Spinner(
                                    children=dbc.CardBody(
                                        children=html.A(
                                            children=html.H2(
                                                id='header-title', 
                                                style={
                                                    'margin': 'auto', 
                                                    'width': '100%', 
                                                    'padding': '0', 
                                                    'text-align': 
                                                    'center'
                                                }
                                            ), 
                                            id='header-link', 
                                            target='_blank'
                                        )
                                    )
                                )
                            ]
                        ), 
                        style=style), 
                    lg=12, 
                    md=12
                ),
            ],
            style=style
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=html.Div(
                        children=[
                            html.Div(
                                children=dbc.Card(
                                    children=[
                                        dbc.CardHeader(
                                            children=html.H4('Sentiment'), 
                                            className='card-title'
                                        ), 
                                        dbc.Spinner(
                                            children=dbc.CardBody(
                                                children=html.H2(
                                                    id='top-card-sentiment', 
                                                    style={
                                                        'margin': 'auto', 
                                                        'width': '50%', 
                                                        'padding': '0', 
                                                        'text-align': 'center'
                                                    }
                                                )
                                            )
                                        )
                                    ]
                                )
                            )
                        ], 
                        style=style
                    ), 
                    lg=4, 
                    md=12
                ),
                dbc.Col(
                    children=html.Div(
                        children=[
                            html.Div(
                                children=dbc.Card(
                                    children=[
                                        dbc.CardHeader(
                                            children=html.H4(
                                                children='Magnitude'), 
                                                className='card-title'
                                            ), 
                                        dbc.Spinner(
                                            children=dbc.CardBody(
                                                children=html.H2(
                                                    id='top-card-magnitude', 
                                                    style={
                                                        'margin': 'auto', 
                                                        'width': '50%', 
                                                        'padding': '0', 
                                                        'text-align': 'center'
                                                    }
                                                )
                                            )
                                        )
                                    ]
                                )
                            )
                        ], 
                        style=style
                    ), 
                    lg=4, 
                    md=12
                ),
                dbc.Col(
                    children=html.Div(
                        children=[
                            html.Div(
                                children=dbc.Card(
                                    children=[
                                        dbc.CardHeader(
                                            children=html.H4('Length'), 
                                            className='card-title'
                                        ), 
                                        dbc.Spinner(
                                            children=dbc.CardBody(
                                                children=html.H2(
                                                    id='top-card-length', 
                                                    style={
                                                        'margin': 'auto', 
                                                        'width': '50%', 
                                                        'padding': '0', 
                                                        'text-align': 'center'
                                                    }
                                                )
                                            )
                                        )
                                    ]
                                )
                            )
                        ], 
                        style=style
                    ), 
                    lg=4, 
                    md=12
                )
            ],
            style=style
        ),        
        dbc.Row(
            children=[
                dbc.Col(
                    children=html.Div(
                        children=dbc.Card(
                            children=[
                                dbc.CardHeader(
                                    children=html.H4(
                                        children='Most important entities'
                                    )
                                ), 
                                dbc.CardBody(
                                    children=dbc.Spinner(
                                        children=chart_entity
                                    )
                                )
                            ]
                        ), 
                        style=style
                    ), 
                    lg=6, 
                    md=12
                ),
                dbc.Col(
                    children=html.Div(
                        children=dbc.Card(
                            children=[
                                dbc.CardHeader(
                                    children=html.H4(
                                        children='Suggested categories'
                                    )
                                ), 
                                dbc.CardBody(
                                    children=dbc.Spinner(
                                        children=chart_category
                                    )
                                )
                            ]
                        ), 
                    style=style
                    ), 
                    lg=6, 
                    md=12
                )
            ],
            style=style
        ),
        dbc.Row(
            children=dbc.Col(
                children=html.Div(
                    children=dbc.Card(
                        children=[
                            dbc.CardHeader(
                                children=html.H4(
                                    children='Sentences by sentiment'
                                )
                            ), 
                            dbc.CardBody(
                                children=dbc.Spinner(
                                    children=html.Div(
                                        id='div-sentences'
                                    )
                                )
                            )
                        ]
                    ), 
                    style=style
                ), 
            lg=12, 
            md=12
        ),
        style=style
    ),
        dbc.Row(
                dbc.Col(
                    children=html.Div(
                        children=dbc.Card(
                            children=[
                                dbc.CardHeader(
                                    children=html.H4(
                                        children='Full text'
                                    )
                                ), 
                                dbc.CardBody(
                                    children=dbc.Spinner(
                                        children=html.Div(
                                            id='div-full-text'
                                        )
                                    )
                                )
                            ]
                        ), 
                        style=style
                    ), 
                    lg=12, 
                    md=12),            
            style=style
        )        
    ],
    style={
        'margin': 'auto',
        'padding': '0px',
        'max-width': '1000px'
    }
)                

@cache.memoize(timeout=timeout)
def get_article(number):
    article = None
    with MongoClient(os.environ['MONGO_CREDENTIALS']) as mongo_client:        
        database = mongo_client['nlp']
        collection = database['articles']
        results = collection.find(
            filter={'number': {'$eq': number}}
        )
    try:
        article = results[0]
        title, text, url = article['title'], article['text'], article['url']
        title = title.strip()
        text = text.strip()
        url = url.strip()
    except Exception as e:
        print(f'{type(e).__name__} : {e} : when getting article from mongod.')
        title, text, url = 'Please try again :(', '', ''
    return title, text, url
 
@cache.memoize(timeout=timeout)
def get_number_of_articles():
    num_documents = 0
    with MongoClient(os.environ['MONGO_CREDENTIALS']) as mongo_client:        
        database = mongo_client['nlp']
        collection = database['articles']
        num_documents = collection.count_documents(filter={})
        print(f'{num_documents} found in mongod.')
    return num_documents

@app.callback(
    [Output('chart-entity', 'figure'),
    Output('chart-category', 'figure'),
    Output('top-card-sentiment', 'children'),
    Output('top-card-magnitude', 'children'),
    Output('top-card-length', 'children'),
    Output('div-sentences', 'children'),
    Output('div-full-text', 'children'),
    Output('header-title', 'children'),
    Output('header-link', 'href')],
    Input('button-next', 'n_clicks')
)
def update(n_clicks):    
    num_documents = get_number_of_articles()
    next_number = random.randint(0, num_documents - 1)
    print(f'displaying results for article number {next_number}.')
    title, text, url = get_article(next_number)

    sentiment_data, overall_sentiment, overall_magnitude = get_sentiment_data(
        title=title, 
        url=url, 
        text=text
    )

    entity_data = get_entity_data(
        title=title, 
        url=url, 
        text=text
    )

    category_data = get_category_data(
        title=title, 
        url=url, 
        text=text
    )

    sentence_list = make_sentence_list(
        data=sentiment_data
    )

    entity_chart = make_entity_chart(entity_data)
    category_chart = make_category_chart(category_data)
    article_card = make_article_card(text)

    outputs = [
        entity_chart, 
        category_chart, 
        f'{overall_sentiment:+0.2f}', 
        f'{overall_magnitude:+0.2f}', 
        len(text.split(' ')), 
        sentence_list, 
        article_card, 
        title, 
        url
    ]

    return outputs

def make_article_card(text):
    article = html.P(
        children=text, 
        style={
            'text-align': 'justify', 
            'text-justify': 'inter-word'
        }
    )
    return article

def make_sentence_list(data):
    children = list()
    for index, row in data.iterrows(): 
        sentiment, magnitude, text = row['Score'], row['Magnitude'], row['Sentence']
        if sentiment_threshold <= sentiment:
            color = color_green
        elif sentiment <= -sentiment_threshold:
            tooltip_text = f'Negative sentiment'
            color = color_red
        else:
            color = color_gray
        alert = dbc.Alert(
            children=text,
            style={
                'background-color': color, 
                'color': '#000000', 
                'text-align': 'justify', 
                'text-justify': 'inter-word'
            }
        )
        children.append(alert)
    return children

@cache.memoize(timeout=timeout)
def get_sentiment_data(title, url, text):
    document = language_v1.Document(
        content=text, 
        type_=language_v1.Document.Type.PLAIN_TEXT
    )
    sentiment = client.analyze_sentiment(request={'document': document})
    overall_sentiment = sentiment.document_sentiment.score
    overall_magnitude = sentiment.document_sentiment.magnitude
    data = list()
    for sentence in sentiment.sentences:
        data.append((sentence.text.content, sentence.sentiment.score, sentence.sentiment.magnitude))
    data = pd.DataFrame(data, columns=['Sentence', 'Score', 'Magnitude'])
    data['Score'] = data['Score'].astype(float)
    data['Magnitude'] = data['Magnitude'].astype(float)
    data.sort_values('Magnitude', inplace=True, ascending=False)
    data = data.head(10)
    data = data.round(4)  
    return data, overall_sentiment, overall_magnitude

@cache.memoize(timeout=timeout)
def get_entity_data(title, url, text):
    document = language_v1.Document(
        content=text, 
        type_=language_v1.Document.Type.PLAIN_TEXT
    )
    entities = client.analyze_entities(request={'document': document})
    data = list()
    for entity in entities.entities:
        data.append((entity.name, entity.salience))
    data = pd.DataFrame(data, columns=['Entity', 'Salience'])
    data = data.groupby('Entity', as_index=False).max()
    data['Salience'] = data['Salience'].astype(float)
    data.sort_values('Salience', inplace=True, ascending=False)
    data = data.head(5)
    data = data.round(4)    
    return data

@cache.memoize(timeout=timeout)
def get_category_data(title, url, text):
    document = language_v1.Document(
        content=text, 
        type_=language_v1.Document.Type.PLAIN_TEXT
    )
    categories = client.classify_text(request={'document': document})
    data = list()
    for category in categories.categories:
        category_short = category.name.split('/')[-1]
        data.append((category_short, category.confidence))
    data = pd.DataFrame(data, columns=['Category', 'Confidence'])
    data['Confidence'] = data['Confidence'].astype(float)
    data.sort_values('Confidence', inplace=True, ascending=False)
    data = data.head(5)
    data = data.round(4)
    return data

def make_entity_chart(data):
    fig = go.Figure()    
    fig.add_trace(
        go.Bar(
            x=data['Entity'], 
            y=data['Salience'],
            marker_line_color='rgb(8,48,107)',
            marker_color='rgb(158,202,225)',
            opacity=0.6            
        )
    )
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=10, r=10, t=5, b=5, pad=5),        
        yaxis_title=('Salience'),
        xaxis_title=('Entity'),
        height=400,
        yaxis=dict(fixedrange=True),
        xaxis=dict(fixedrange=True)        
    )    
    return fig

def make_category_chart(data):
    fig = go.Figure()    
    fig.add_trace(
        go.Bar(
            x=data['Category'], 
            y=data['Confidence'],
            marker_line_color='rgb(8,48,107)',
            marker_color='rgb(158,202,225)',
            opacity=0.6
        )        
    )
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=10, r=10, t=5, b=5, pad=5),        
        yaxis_title=('Confidence'),                
        xaxis_title=('Category'),
        height=400,
        yaxis_range=[0, 1],
        yaxis=dict(fixedrange=True),
        xaxis=dict(
            fixedrange=True,
            categoryorder='array',
            categoryarray=data['Category'].reset_index().index.to_list()
        )
    )        
    return fig    

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)