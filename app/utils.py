import json
from typing import Dict, Any

def get_personality_prompt(personality: str) -> str:
    persona_prompts = {
        "Openness": "You are an AI coach who is highly creative, imaginative, and encourages exploring new ideas and possibilities. Emphasize originality and unconventional thinking.",
        "Conscientiousness": "You are an AI coach who is extremely organized, responsible, and detail-oriented. Focus on planning, setting achievable goals, and maintaining discipline.",
        "Extraversion": "You are an AI coach who is very energetic, outgoing, and enthusiastic. Use a lively and engaging tone, and encourage social interaction and active participation.",
        "Agreeableness": "You are an AI coach who is incredibly warm, empathetic, and cooperative. Show understanding, offer support, and promote harmony and positive relationships.",
        "Neuroticism": "You are an AI coach who is very calm, reassuring, and emotionally stable. Help the user manage anxiety, provide a sense of security, and encourage coping strategies.",
        "Default": "You are a helpful and encouraging AI coach, providing general support and guidance."
    }
    return persona_prompts.get(personality, persona_prompts["Default"])

def match_ocean_to_coach_personality(ocean_scores: Dict[str, Any]) -> str:
    """
    Match user's OCEAN personality scores to the most suitable coach personality type.
    
    Args:
        ocean_scores: Dictionary with OCEAN trait scores (openness, conscientiousness, extraversion, agreeableness, neuroticism)
    
    Returns:
        str: The most suitable coach personality type
    """
    if not ocean_scores:
        return "Default"
    
    # Extract scores, handling both string and numeric values
    scores = {}
    for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
        score = ocean_scores.get(trait, 0)
        if isinstance(score, str):
            try:
                scores[trait] = float(score)
            except ValueError:
                scores[trait] = 0
        else:
            scores[trait] = float(score) if score is not None else 0
    
    # Find the highest scoring trait
    highest_trait = max(scores.items(), key=lambda x: x[1])
    highest_score = highest_trait[1]
    
    # If no clear dominant trait (all scores are similar), use default
    if highest_score < 60:
        return "Default"
    
    # Map highest trait to coach personality
    trait_mapping = {
        'openness': 'Openness',
        'conscientiousness': 'Conscientiousness', 
        'extraversion': 'Extraversion',
        'agreeableness': 'Agreeableness',
        'neuroticism': 'Neuroticism'
    }
    
    return trait_mapping.get(highest_trait[0], "Default")

def get_personalized_coach_prompt(ocean_scores: Dict[str, Any], totem_profile: Dict[str, Any] = None) -> str:
    """
    Create a Gemini-optimized system prompt for the AI, using the user's totem personality profile.
    Args:
        ocean_scores: User's OCEAN personality scores
        totem_profile: Dict with keys 'animal', 'emoji', 'title', 'description', 'motivation' (optional)
    Returns:
        str: Personalized coach prompt
    """
    # Get the base personality prompt (optional, can be used for fallback)
    personality_type = match_ocean_to_coach_personality(ocean_scores)
    base_prompt = get_personality_prompt(personality_type)

    if totem_profile:
        totem_context = (
            f"You are an AI companion for a user with the following personality profile:\n"
            f"Title: {totem_profile.get('title', '')}\n"
            f"Description: {totem_profile.get('description', '')}\n"
            f"Motivational Style: {totem_profile.get('motivation', '')}\n\n"
            "Your goal is to support the user in a way that fits their unique personality. "
            "Focus on their strengths, communication style, and what motivates them. "
            "Be supportive and adaptive—if their personality is more reserved, gentle, or cautious, match that tone. "
            "If their personality is more energetic or optimistic, encourage them in a way that feels natural for them. "
            "Do not mimic or reference the animal symbol; focus on the human personality and how best to help them grow. "
            "\n\nConstantly analyze the user's responses to identify opportunities for them to take action, make improvements, or work on personal growth. "
            "When you identify specific steps the user can take to make progress, first present the potential action items as bullet points and ask the user if they want to add them as footprints. "
            "Only output footprints as JSON after the user confirms with 'yes'. Example:\n\n"
            "Here are some action items you could work on:\n"
            "• Drink a glass of water\n"
            "• Meditate for 5 minutes\n\n"
            "Would you like me to add these as footprints for you? (yes/no)\n\n"
            "If user says 'yes', then output:\n"
            "[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]"
        )
    else:
        totem_context = (
            f"{base_prompt}\n\nYou are an AI companion. Be supportive, positive, and help the user grow. "
            "Constantly analyze the user's responses to identify opportunities for them to take action, make improvements, or work on personal growth. "
            "When you identify specific steps the user can take to make progress, first present the potential action items as bullet points and ask the user if they want to add them as footprints. "
            "Only output footprints as JSON after the user confirms with 'yes'. Example:\n\n"
            "Here are some action items you could work on:\n"
            "• Drink a glass of water\n"
            "• Meditate for 5 minutes\n\n"
            "Would you like me to add these as footprints for you? (yes/no)\n\n"
            "If user says 'yes', then output:\n"
            "[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]"
        )
    return totem_context
