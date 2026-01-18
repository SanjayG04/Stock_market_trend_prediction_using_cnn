import yfinance as yf

class FundamentalAnalyzer:
    """Fundamental analysis using financial ratios"""
    
    def __init__(self):
        self.weights = {
            'pe_ratio': 10,
            'peg_ratio': 10,
            'roe': 10,
            'debt_equity': 10,
            'pb_ratio': 10
        }
    
    def fetch_stock_data(self, ticker):
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def calculate_scores(self, metrics):
        """Calculate scores for each metric"""
        scores = {}
        
        # P/E Ratio (lower is better, typically < 25 is good)
        pe = metrics.get('pe_ratio', 0)
        if pe > 0:
            if pe < 15:
                scores['pe_ratio'] = 10
            elif pe < 25:
                scores['pe_ratio'] = 7
            elif pe < 35:
                scores['pe_ratio'] = 4
            else:
                scores['pe_ratio'] = 2
        else:
            scores['pe_ratio'] = 0
        
        # PEG Ratio (< 1 is undervalued)
        peg = metrics.get('peg_ratio', 0)
        if peg > 0:
            if peg < 1:
                scores['peg_ratio'] = 10
            elif peg < 2:
                scores['peg_ratio'] = 6
            else:
                scores['peg_ratio'] = 3
        else:
            scores['peg_ratio'] = 0
        
        # ROE (higher is better, > 15% is good)
        roe = metrics.get('roe', 0)
        if roe > 20:
            scores['roe'] = 10
        elif roe > 15:
            scores['roe'] = 7
        elif roe > 10:
            scores['roe'] = 5
        else:
            scores['roe'] = 2
        
        # Debt-to-Equity (lower is better, < 1 is good)
        de = metrics.get('debt_equity', 0)
        if de < 0.5:
            scores['debt_equity'] = 10
        elif de < 1:
            scores['debt_equity'] = 7
        elif de < 2:
            scores['debt_equity'] = 4
        else:
            scores['debt_equity'] = 2
        
        # P/B Ratio (lower is better, < 3 is good)
        pb = metrics.get('pb_ratio', 0)
        if pb > 0:
            if pb < 1:
                scores['pb_ratio'] = 10
            elif pb < 3:
                scores['pb_ratio'] = 7
            elif pb < 5:
                scores['pb_ratio'] = 4
            else:
                scores['pb_ratio'] = 2
        else:
            scores['pb_ratio'] = 0
        
        return scores
    
    def analyze(self, ticker):
        """Perform fundamental analysis"""
        info = self.fetch_stock_data(ticker)
        
        if not info:
            return None
        
        # Extract metrics
        metrics = {
            'pe_ratio': info.get('trailingPE', 0) or info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
            'debt_equity': info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0,
            'pb_ratio': info.get('priceToBook', 0)
        }
        
        # Calculate scores
        scores = self.calculate_scores(metrics)
        total_score = sum(scores.values())
        
        result = {
            'pe_ratio': metrics['pe_ratio'],
            'peg_ratio': metrics['peg_ratio'],
            'roe': metrics['roe'],
            'debt_equity': metrics['debt_equity'],
            'pb_ratio': metrics['pb_ratio'],
            'scores': scores,
            'score': total_score,
            'company_name': info.get('longName', ticker)
        }
        
        return result
