from typing import List

class ActionRecommendationAgent:
    def recommend(self, strategy: str) -> List[str]:
        # Simple parsing: split strategy into steps
        actions = strategy.split('. ')
        return [action.strip() for action in actions if action.strip()]