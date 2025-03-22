# app/models/dynamic_events.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import streamlit as st
import json

class DynamicEventGenerator:
    def __init__(self):
        self.event_components = {
            "prefixes": [
                "Mysterious", "Ancient", "Divine", "Chaotic", "Harmonious",
                "Celestial", "Shadow", "Elemental", "Temporal", "Ethereal"
            ],
            "core_names": [
                "Blessing", "Challenge", "Trial", "Awakening", "Convergence",
                "Phenomenon", "Revelation", "Surge", "Manifestation", "Resonance"
            ],
            "effects": {
                "attribute_boost": {
                    "name": "Attribute Boost",
                    "description": "Increases {attribute} gains by {magnitude}%",
                    "magnitude_range": (20, 100)
                },
                "multi_attribute": {
                    "name": "Multi-Attribute Enhancement",
                    "description": "Increases all attribute gains by {magnitude}%",
                    "magnitude_range": (10, 50)
                },
                "task_bonus": {
                    "name": "Task Bonus",
                    "description": "Completed tasks give {magnitude}% more points",
                    "magnitude_range": (25, 75)
                },
                "streak_multiplier": {
                    "name": "Streak Power",
                    "description": "Streak multiplier increased by {magnitude}%",
                    "magnitude_range": (15, 60)
                },
                "recovery_boost": {
                    "name": "Recovery Boost",
                    "description": "Reduces penalty duration by {magnitude}%",
                    "magnitude_range": (20, 50)
                }
            },
            "conditions": {
                "time_based": {
                    "morning_rush": "Active during morning hours (6 AM - 10 AM)",
                    "night_owl": "Active during night hours (10 PM - 2 AM)",
                    "golden_hour": "Active for one hour"
                },
                "streak_based": {
                    "streak_maintained": "Remains active while streak is maintained",
                    "streak_milestone": "Activates at streak milestones"
                },
                "performance_based": {
                    "perfect_day": "Requires completing all daily tasks",
                    "attribute_threshold": "Requires reaching specific attribute levels"
                }
            },
            "durations": [1, 3, 6, 12, 24],  # hours
            "rarities": {
                "Common": {"weight": 50, "color": "#808080"},
                "Uncommon": {"weight": 30, "color": "#00FF00"},
                "Rare": {"weight": 15, "color": "#0000FF"},
                "Epic": {"weight": 4, "color": "#800080"},
                "Legendary": {"weight": 1, "color": "#FFD700"}
            }
        }

    def generate_event(self, user_data: Dict) -> Dict:
        """Generate a random dynamic event based on user state"""
        # Select event components
        prefix = random.choice(self.event_components["prefixes"])
        core_name = random.choice(self.event_components["core_names"])
        effect_type = random.choice(list(self.event_components["effects"].keys()))
        condition_type = random.choice(list(self.event_components["conditions"].keys()))
        duration = random.choice(self.event_components["durations"])
        rarity = self.select_rarity()

        # Generate effect details
        effect = self.generate_effect(effect_type, user_data)
        condition = self.generate_condition(condition_type, user_data)

        # Create event
        event = {
            "id": f"event_{datetime.now().timestamp()}",
            "name": f"{prefix} {core_name}",
            "effect": effect,
            "condition": condition,
            "duration": duration,
            "rarity": rarity,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "completed": False
        }

        return self.enhance_event(event, user_data)

    def generate_effect(self, effect_type: str, user_data: Dict) -> Dict:
        """Generate specific effect details"""
        effect_template = self.event_components["effects"][effect_type]
        magnitude = random.randint(*effect_template["magnitude_range"])

        if effect_type == "attribute_boost":
            attribute = random.choice(list(user_data["attributes"].keys()))
            description = effect_template["description"].format(
                attribute=attribute,
                magnitude=magnitude
            )
            effect = {
                "type": effect_type,
                "attribute": attribute,
                "magnitude": magnitude,
                "description": description
            }
        else:
            description = effect_template["description"].format(magnitude=magnitude)
            effect = {
                "type": effect_type,
                "magnitude": magnitude,
                "description": description
            }

        return effect

    def generate_condition(self, condition_type: str, user_data: Dict) -> Dict:
        """Generate specific condition details"""
        conditions = self.event_components["conditions"][condition_type]
        condition_key = random.choice(list(conditions.keys()))
        
        condition = {
            "type": condition_type,
            "key": condition_key,
            "description": conditions[condition_key]
        }

        if condition_type == "performance_based":
            if condition_key == "attribute_threshold":
                attribute = random.choice(list(user_data["attributes"].keys()))
                current_value = user_data["attributes"][attribute]
                threshold = current_value + random.randint(20, 50)
                condition["attribute"] = attribute
                condition["threshold"] = threshold
                condition["description"] = f"Reach {threshold} points in {attribute}"

        return condition

    def select_rarity(self) -> str:
        """Select event rarity based on weights"""
        rarities = list(self.event_components["rarities"].keys())
        weights = [self.event_components["rarities"][r]["weight"] for r in rarities]
        return random.choices(rarities, weights=weights)[0]

    def enhance_event(self, event: Dict, user_data: Dict) -> Dict:
        """Enhance event based on user progress and current state"""
        # Add visual elements
        event["color"] = self.event_components["rarities"][event["rarity"]]["color"]
        event["icon"] = self.get_event_icon(event)

        # Add challenge elements
        if random.random() < 0.3:  # 30% chance for additional challenge
            event["challenge"] = self.generate_challenge(user_data)
            event["bonus_reward"] = self.generate_bonus_reward(event["rarity"])

        return event

    def get_event_icon(self, event: Dict) -> str:
        """Select appropriate icon for event"""
        icon_map = {
            "attribute_boost": "⚡",
            "multi_attribute": "✨",
            "task_bonus": "🎯",
            "streak_multiplier": "🔥",
            "recovery_boost": "💫"
        }
        return icon_map.get(event["effect"]["type"], "🎲")

    def generate_challenge(self, user_data: Dict) -> Dict:
        """Generate additional challenge for event"""
        challenges = [
            {
                "type": "task_streak",
                "description": "Complete all tasks for {count} days",
                "count": random.randint(2, 5)
            },
            {
                "type": "attribute_gain",
                "description": "Gain {count} points in {attribute}",
                "attribute": random.choice(list(user_data["attributes"].keys())),
                "count": random.randint(10, 30)
            },
            {
                "type": "perfect_timing",
                "description": "Complete tasks within specific time windows",
                "windows": self.generate_time_windows()
            }
        ]
        
        challenge = random.choice(challenges)
        if challenge["type"] == "task_streak":
            challenge["description"] = challenge["description"].format(
                count=challenge["count"]
            )
        elif challenge["type"] == "attribute_gain":
            challenge["description"] = challenge["description"].format(
                count=challenge["count"],
                attribute=challenge["attribute"]
            )
            
        return challenge

    def generate_time_windows(self) -> List[Dict]:
        """Generate time windows for time-based challenges"""
        windows = []
        for _ in range(random.randint(2, 4)):
            start_hour = random.randint(6, 20)
            duration = random.randint(1, 3)
            windows.append({
                "start": f"{start_hour:02d}:00",
                "end": f"{(start_hour + duration):02d}:00"
            })
        return windows

    def generate_bonus_reward(self, rarity: str) -> Dict:
        """Generate bonus reward for completing challenge"""
        reward_scales = {
            "Common": 1,
            "Uncommon": 1.5,
            "Rare": 2,
            "Epic": 3,
            "Legendary": 5
        }
        
        scale = reward_scales[rarity]
        return {
            "attribute_points": int(10 * scale),
            "streak_bonus": round(0.1 * scale, 2),
            "description": f"Bonus: +{int(10 * scale)} to all attributes and {round(0.1 * scale, 2)}x streak multiplier"
        }

    def check_event_completion(self, event: Dict, user_data: Dict) -> bool:
        """Check if event conditions are met"""
        condition = event["condition"]
        
        if condition["type"] == "time_based":
            return self.check_time_condition(condition)
        elif condition["type"] == "streak_based":
            return self.check_streak_condition(condition, user_data)
        elif condition["type"] == "performance_based":
            return self.check_performance_condition(condition, user_data)
            
        return False

    def check_time_condition(self, condition: Dict) -> bool:
        """Check time-based conditions"""
        current_time = datetime.now()
        if condition["key"] == "morning_rush":
            return 6 <= current_time.hour <= 10
        elif condition["key"] == "night_owl":
            return current_time.hour >= 22 or current_time.hour <= 2
        return True

    def check_streak_condition(self, condition: Dict, user_data: Dict) -> bool:
        """Check streak-based conditions"""
        if condition["key"] == "streak_maintained":
            return user_data["streak"] > 0
        elif condition["key"] == "streak_milestone":
            return user_data["streak"] in [7, 14, 30, 60, 90]
        return False

    def check_performance_condition(self, condition: Dict, user_data: Dict) -> bool:
        """Check performance-based conditions"""
        if condition["key"] == "perfect_day":
            return all(task["completed"] for task in user_data["tasks"]["daily"].values())
        elif condition["key"] == "attribute_threshold":
            return user_data["attributes"][condition["attribute"]] >= condition["threshold"]
        return False

    def apply_event_effects(self, event: Dict, user_data: Dict):
        """Apply event effects to user data"""
        effect = event["effect"]
        
        if effect["type"] == "attribute_boost":
            if "attribute_multipliers" not in user_data:
                user_data["attribute_multipliers"] = {}
            user_data["attribute_multipliers"][effect["attribute"]] = 1 + (effect["magnitude"] / 100)
            
        elif effect["type"] == "multi_attribute":
            for attribute in user_data["attributes"]:
                if "attribute_multipliers" not in user_data:
                    user_data["attribute_multipliers"] = {}
                user_data["attribute_multipliers"][attribute] = 1 + (effect["magnitude"] / 100)
                
        elif effect["type"] == "task_bonus":
            user_data["task_multiplier"] = 1 + (effect["magnitude"] / 100)
            
        elif effect["type"] == "streak_multiplier":
            if "multipliers" not in user_data:
                user_data["multipliers"] = {}
            user_data["multipliers"]["streak"] = 1 + (effect["magnitude"] / 100)
            
        elif effect["type"] == "recovery_boost":
            user_data["penalty_reduction"] = effect["magnitude"] / 100

    def display_event(self, event: Dict):
        """Display event card"""
        st.markdown(f"""
            <div class="event-card {event['rarity'].lower()}" style="border-color: {event['color']}">
                <div class="event-header">
                    <span class="event-icon">{event['icon']}</span>
                    <h3>{event['name']}</h3>
                    <span class="event-rarity">{event['rarity']}</span>
                </div>
                <div class="event-effect">
                    <p>{event['effect']['description']}</p>
                </div>
                <div class="event-condition">
                    <h4>Condition:</h4>
                    <p>{event['condition']['description']}</p>
                </div>
                {self.format_challenge(event) if 'challenge' in event else ''}
                <div class="event-duration">
                    Duration: {event['duration']} hours
                </div>
            </div>
        """, unsafe_allow_html=True)

    def format_challenge(self, event: Dict) -> str:
        """Format challenge section for display"""
        challenge = event['challenge']
        return f"""
            <div class="event-challenge">
                <h4>Bonus Challenge:</h4>
                <p>{challenge['description']}</p>
                <div class="challenge-reward">
                    {event['bonus_reward']['description']}
                </div>
            </div>
        """