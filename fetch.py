# from dotenv import load_dotenv # to load API key
# import pandas as pd
import requests
import os
import datetime
from datetime import timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# load_dotenv()

from sqlalchemy.orm import Session
from models import *

# Loading the API key from environment variable
# We want to hide keys into a .env (not uploaded to GitHub)
# NEWS_API_KEY=os.getenv('NEWS_API_KEY')

# use newsapi to get news article data
# https://newsapi.org/
# !pip install newsapi-python
# from newsapi import NewsApiClient
# newsapi=NewsApiClient(api_key=NEWS_API_KEY)

# documentation: https://newsapi.org/docs/endpoints/everything
# return a dictionary (JSON)
# get news article for BTC and ETH
# btc_headlines=newsapi.get_everything(
#                 q='bitcoin', 
#                 language='en', 
#                 sort_by='relevancy', 
#                 from_param='2021-05-17'
#                 )
class News_Api(): 
	def __init__(self, apiKey): 
		self.apiKey=apiKey
		return None

	def get_recent_news(self, engine, topic): 
		session=Session(engine)
		base_url='https://newsapi.org/v2/everything?'
		time_now=datetime.datetime.utcnow()
		five_minutes_ago=time_now-timedelta(minutes=5)
		query_params={'q': topic, 
					  'language': 'en', 
					  'sortBy': 'publishedAt', 
					  'from': five_minutes_ago.strftime("%Y-%m-%dT%H:%M:%SZ"), 
					  'apiKey': self.apiKey}
		response=requests.get(base_url, params=query_params)
		results=response.json()
		# print(results)
		# print(len(data))
		analyzer=SentimentIntensityAnalyzer()
		# articles=[]
		for each_article in results['articles']:
			if each_article['publishedAt']>five_minutes_ago: 
				try: 
					text=each_article['content']
					score=analyzer.polarity_scores(text)
					news={
						'processed': time_now.strftime("%Y-%m-%dT%H:%M:%SZ"), 
						'source': each_article['source']['name'], 
						'author': each_article['author'], 
						'title': each_article['title'], 
						'description': each_article['description'], 
						'url': each_article['url'], 
						'publishedAt': each_article['publishedAt'], 
						'content': each_article['content'], 
						'compound_score': score['compound'], 
						'neutral_score': score['neu'], 
						'positive_score': score['pos'], 
						'negative_score': score['neg']
						}
					session.add(News(**news))
				except AttributeError: 
					print('error')
		session.commit()
		session.close()			
		return None

# print(len(get_news('tesla')))


# url=base_url+'q=tesla&from=2021-04-17&sortBy=publishedAt&apiKey=API_KEY'


# # convert data into a Pandas DataFrame
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# analyzer=SentimentIntensityAnalyzer()
# articles=[]
# for each_article in btc_headlines['articles']: 
#     try: 
#         text=each_article['content']
#         score=analyzer.polarity_scores(text)
#         articles.append({'article': text, 'score': score['compound']})
#     except AttributeError: 
#         print('error')
#         pass

# btc=pd.DataFrame(articles)
# btc.head()