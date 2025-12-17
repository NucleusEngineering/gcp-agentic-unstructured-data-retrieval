from src.agents.prompt_strategies import ALL_STRATEGIES, PromptStrategy

def choose_strategy(user_query: str) -> PromptStrategy:
    q = (user_query or "").strip()
    for strat in ALL_STRATEGIES:
        if strat.match(q):
            return strat
    return ALL_STRATEGIES[-1]
