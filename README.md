
# [Natural Language Processing with Google](https://news-articles-nlp.herokuapp.com)

## Project goal
The goal of this project is to build a `responsive dashborad`
that will display the results of text analysis. The text analysis is performed by the Google NLP service. [The dashboard is hosted on heroku](https://news-articles-nlp.herokuapp.com/).

### Methods
* Sentiment analysis
* Entity analysis
* Text classification

### Technologies
* Python
* newspaper3k
* Dash
* Plotly
* MongoDB
* Google Cloud Platform
* Google NLP API

## Project description
The server chooses a random article from a `MongoDB` collection, sends it to the `Google NLP API` for analysis and displays information about the documents sentiment, salient entities and possible categories.
The results are cached by the server in to ensure quicker load times.