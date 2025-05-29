from sec_api import QueryApi
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import List, Dict

class ScraperAgent:
    def __init__(self, sec_api_key: str, news_url: str, debug: bool = False):
        self.news_url = news_url
        self.sec_api_key = sec_api_key
        self.query_api = QueryApi(api_key=self.sec_api_key)
        self.debug = debug

    def doc_combined(self, tickers: List[str]) -> Dict[str, str]:
        new_docs = {}
        try:
            doc1 = self.scrape_news(tickers)
            doc2 = self.scrape_earnings_sec(tickers)
            for ticker in tickers:
                combined = f"{doc2.get(ticker, 'No earnings data.')}\n\n{doc1.get(ticker, 'No news data.')}"
                new_docs[ticker] = combined
        except Exception as e:
            for ticker in tickers:
                new_docs[ticker] = f"Error combining data: {str(e)}"
        return new_docs

    def scrape_news(self, tickers: List[str]) -> Dict[str, str]:
        results = {}
        try:
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(self.news_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
            articles = soup.find_all('article')

            for ticker in tickers:
                snippets = []
                for article in articles:
                    text = article.get_text().lower()
                    if ticker.lower() in text:
                        snippets.append(text.strip()[:500])
                if snippets:
                    results[ticker] = "\n\n".join(snippets)
                else:
                    results[ticker] = 'No relevant news found.'

                if self.debug:
                    print(f"[DEBUG] News for {ticker}: {results[ticker][:500]}")
        except Exception as e:
            for ticker in tickers:
                results[ticker] = f"Error scraping news: {str(e)}"
        return results

    def scrape_earnings_sec(self, tickers: List[str]) -> Dict[str, str]:
        results = {}
        for ticker in tickers:
            try:
                query_params = {
                    'query': f'ticker:{ticker} AND formType:"10-Q"',
                    'from': '0',
                    'size': '3'
                }
                filings = self.query_api.get_filings(query_params)
                if filings.get('filings'):
                    descriptions = [
                        filing.get('description', '') for filing in filings['filings']
                    ]
                    combined = "\n\n".join([f"{ticker} 10-Q: {desc}" for desc in descriptions if desc])
                    results[ticker] = combined or 'No descriptions found.'
                else:
                    results[ticker] = 'No earnings report found.'

                if self.debug:
                    print(f"[DEBUG] SEC for {ticker}: {results[ticker][:500]}")
            except Exception as e:
                results[ticker] = f"Error fetching SEC earnings: {str(e)}"
        return results
