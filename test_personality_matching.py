#!/usr/bin/env python3
"""
Test script for personality matching functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils import match_ocean_to_coach_personality, get_personalized_coach_prompt

def test_personality_matching():
    """Test the personality matching functionality"""
    
    print("🧪 Testing Personality Matching System")
    print("=" * 50)
    
    # Test cases with different OCEAN scores
    test_cases = [
        {
            "name": "High Openness",
            "scores": {"openness": 85, "conscientiousness": 45, "extraversion": 60, "agreeableness": 70, "neuroticism": 30}
        },
        {
            "name": "High Conscientiousness", 
            "scores": {"openness": 40, "conscientiousness": 90, "extraversion": 50, "agreeableness": 65, "neuroticism": 35}
        },
        {
            "name": "High Extraversion",
            "scores": {"openness": 60, "conscientiousness": 55, "extraversion": 88, "agreeableness": 75, "neuroticism": 25}
        },
        {
            "name": "High Agreeableness",
            "scores": {"openness": 55, "conscientiousness": 60, "extraversion": 65, "agreeableness": 92, "neuroticism": 20}
        },
        {
            "name": "High Neuroticism",
            "scores": {"openness": 45, "conscientiousness": 50, "extraversion": 40, "agreeableness": 60, "neuroticism": 85}
        },
        {
            "name": "Balanced (Default)",
            "scores": {"openness": 55, "conscientiousness": 52, "extraversion": 58, "agreeableness": 54, "neuroticism": 51}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📊 {test_case['name']}:")
        print(f"   Scores: {test_case['scores']}")
        
        # Test personality matching
        personality_type = match_ocean_to_coach_personality(test_case['scores'])
        print(f"   → Matched Coach Type: {personality_type}")
        
        # Test personalized prompt
        prompt = get_personalized_coach_prompt(
            test_case['scores'], 
            totem_animal="Dolphin", 
            totem_title="The Explorer"
        )
        print(f"   → Prompt Length: {len(prompt)} characters")
        print(f"   → Prompt Preview: {prompt[:100]}...")
    
    print("\n✅ Personality matching tests completed!")

if __name__ == "__main__":
    test_personality_matching() 