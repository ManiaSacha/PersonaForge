from typing import Dict

def generate_prompt(persona: Dict, user_input: str) -> str:
    goals_formatted = "\n".join([f"- {goal}" for goal in persona["goals"]])

    prompt = f"""You are {persona['name']}, an AI specialized in {persona['domain']}.
Your tone should be {persona['tone']} and your responses must be in a {persona['response_style']} style.
Your main goals are:
{goals_formatted}

User query: {user_input}
"""
    return prompt
