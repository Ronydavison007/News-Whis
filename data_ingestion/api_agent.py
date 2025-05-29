from alpha_vantage.timeseries import TimeSeries
from yfinance import Ticker
from typing import Dict, Any, List

class DataIngestionAPIAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.ts = TimeSeries(key=self.api_key, output_format='json', indexing_type='date')
    
    def fetch_stock_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        results = {}
        for symbol in symbols:
            try:
                data, _ = self.ts.get_quote_endpoint(symbol=symbol)  # Unpack tuple
                if data:
                    results[symbol] = {
                        'open': float(data['02. open']),
                        'high': float(data['03. high']),
                        'low': float(data['04. low']),
                        'price': float(data['05. price']),
                        'volume': float(data['06. volume']),
                        'previous close': float(data['08. previous close']),
                        'change': float(data['09. change']),
                        'change percent': str(data['10. change percent'])
                    }
                else:
                    raise ValueError("No data returned from Alpha Vantage")
            except Exception as e:
                try:
                    yf = Ticker(symbol)
                    hist = yf.history(period='1d')
                    if not hist.empty:
                        latest = hist.iloc[-1]
                        results[symbol] = {
                            'open': float(latest['Open']),
                            'high': float(latest['High']),
                            'low': float(latest['Low']),
                            'price': float(latest['Close']),
                            'volume': float(latest['Volume']),
                            'previous close': float(hist['Close'].iloc[-2]) if len(hist) > 1 else float(latest['Open']),
                            'change': float(latest['Close']) - float(latest['Open']),
                            'change percent': f"{((latest['Close'] - latest['Open']) / latest['Open']) * 100:.2f}%"
                        }
                    else:
                        results[symbol] = {'error': 'No data available'}
                except Exception as yf_e:
                    results[symbol] = {'error': f"Alpha Vantage error: {e}, yfinance error: {yf_e}"}
        return results
