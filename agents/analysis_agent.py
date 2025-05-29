from typing import Dict, Any

class AnalyticsAgent:
    def __init__(self, data: Dict[str, Dict[str, Any]]):
        self.data = data
        self.prev_avg_vol = 3_000_000  # Shared baseline volume

    def analysis(self) -> Dict[str, Any]:
        results = {}
        try:
            if not self.data or not isinstance(self.data, dict):
                raise ValueError("Invalid data format")
            
            # Hardcoded portfolio weights (replace with real data)
            weights = {ticker: 1/len(self.data) for ticker in self.data}  # Equal weights
            total_allocation = 0
            change_summary = []
            
            for ticker, info in self.data.items():
                try:
                    if 'error' in info:
                        results[ticker] = f"Error: {info['error']}"
                        continue
                    open_profit = info['price'] - info['open']
                    prev_close_profit = info['price'] - info['previous close']
                    volatility = info['high'] - info['low']
                    intra_risk_est = (volatility / info['open']) * 100

                    change_percent = float(str(info['change percent']).strip('%'))
                    momentum = 'Bullish' if change_percent > 2.0 else 'Bearish' if change_percent < -2.0 else 'Neutral'
                    volume_analysis = 'High liquidity' if int(info['volume']) > self.prev_avg_vol else 'Low liquidity'
                    if int(info['volume']) > self.prev_avg_vol:
                        self.prev_avg_vol = (info['volume'] + self.prev_avg_vol) / 2

                    # Calculate allocation contribution
                    allocation = weights[ticker] * info['price'] / sum(weights[t] * self.data[t]['price'] for t in self.data if 'error' not in self.data[t]) * 100
                    total_allocation += allocation
                    change_summary.append(f"{ticker}: {change_percent:.2f}%")

                    results[ticker] = {
                        'open_profit': open_profit,
                        'prev_close_profit': prev_close_profit,
                        'intra_risk_est': intra_risk_est,
                        'momentum': momentum,
                        'volume_analysis': volume_analysis,
                        'allocation': allocation
                    }
                except Exception as e:
                    results[ticker] = f"Error processing {ticker}: {str(e)}"

            results['portfolio'] = {
                'allocation': round(total_allocation, 2),
                'change': f"change based on {', '.join(change_summary)}",
                'sentiment': 'Neutral'  # Simplified, replace with NLP if needed
            }
            return results
        except Exception as e:
            raise ValueError(f"Analysis error: {str(e)}")
