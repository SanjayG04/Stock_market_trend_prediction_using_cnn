class ScoringEngine:
    """Combine technical and fundamental analysis"""
    
    def __init__(self):
        self.technical_weight = 0.5  # 50% weight
        self.fundamental_weight = 0.5  # 50% weight
    
    def combine_scores(self, technical_result, fundamental_result):
        """Combine scores and generate recommendation"""
        
        # Get scores
        tech_score = technical_result['score']
        fund_score = fundamental_result['score']
        
        # Calculate weighted final score (0-100)
        final_score = (tech_score + fund_score)
        
        # Determine recommendation
        if final_score >= 80:
            recommendation = "STRONG BUY"
            reasoning = "Excellent fundamentals combined with strong bullish trend. High confidence investment opportunity."
        elif final_score >= 65:
            recommendation = "BUY"
            reasoning = "Good fundamentals and positive technical signals. Favorable entry point."
        elif final_score >= 50:
            recommendation = "HOLD"
            reasoning = "Mixed signals from technical and fundamental analysis. Consider waiting for clearer trend."
        elif final_score >= 35:
            recommendation = "SELL"
            reasoning = "Weak fundamentals or bearish technical trend. Consider reducing position."
        else:
            recommendation = "STRONG SELL"
            reasoning = "Poor fundamentals and negative technical signals. High risk of losses."
        
        # Additional context based on components
        if tech_score > 40 and fund_score < 30:
            reasoning += " Note: Strong technical trend but weak fundamentals - suitable for short-term trades only."
        elif fund_score > 40 and tech_score < 30:
            reasoning += " Note: Strong fundamentals but weak technical trend - good for long-term accumulation."
        
        result = {
            'final_score': round(final_score, 2),
            'recommendation': recommendation,
            'reasoning': reasoning,
            'technical_score': tech_score,
            'fundamental_score': fund_score
        }
        
        return result
