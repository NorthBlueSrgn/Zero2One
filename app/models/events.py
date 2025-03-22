# app/models/events.py
from typing import Dict, Optional
from datetime import datetime, timedelta
import random
import streamlit as st

class SpecialEvents:
    def __init__(self):
        self.events = {
            # Positive Events
            "double_points": {
                "name": "Double Points",
                "description": "All tasks give double points!",
                "duration": 24,  # hours
                "multiplier": 2.0,
                "icon": "✨",
                "rarity": "Common",
                "trigger_chance": 0.1,  # 10% daily chance
                "type": "positive",
                "effects": {
                    "point_multiplier": 2.0
                }
            },
            "attribute_surge": {
                "name": "Attribute Surge",
                "description": "Random attribute gains +50% points",
                "duration": 12,
                "multiplier": 1.5,
                "icon": "💫",
                "rarity": "Uncommon",
                "trigger_chance": 0.05,
                "type": "positive",
                "effects": {
                    "attribute_boost": 1.5
                }
            },
            "golden_hour": {
                "name": "Golden Hour",
                "description": "All attributes gain +100% points for 1 hour",
                "duration": 1,
                "multiplier": 2.0,
                "icon": "⚡",
                "rarity": "Rare",
                "trigger_chance": 0.02,
                "type": "positive",
                "effects": {
                    "all_attributes_boost": 2.0
                }
            },
            "streak_power": {
                "name": "Streak Power",
                "description": "Streak multiplier doubled",
                "duration": 24,
                "multiplier": 2.0,
                "icon": "🔥",
                "rarity": "Epic",
                "trigger_chance": 0.01,
                "type": "positive",
                "effects": {
                    "streak_multiplier": 2.0
                }
            },

            # Challenge Events
            "perfect_day": {
                "name": "Perfect Day Challenge",
                "description": "Complete all tasks perfectly for bonus rewards",
                "duration": 24,
                "icon": "🎯",
                "rarity": "Uncommon",
                "trigger_chance": 0.05,
                "type": "challenge",
                "success_reward": {
                    "all_attributes": 5,
                    "streak_bonus": 1
                },
                "failure_penalty": {
                    "streak_reduction": 1
                }
            },
            "speed_runner": {
                "name": "Speed Runner Challenge",
                "description": "Complete all daily tasks within 6 hours",
                "duration": 6,
                "icon": "⚡",
                "rarity": "Rare",
                "trigger_chance": 0.03,
                "type": "challenge",
                "success_reward": {
                    "all_attributes": 10,
                    "point_multiplier": 2.0
                },
                "failure_penalty": {
                    "point_reduction": 5
                }
            }
        }

    def check_for_events(self, user_data: Dict):
        """Check for random event triggers"""
        current_time = datetime.now()
        last_check = datetime.fromisoformat(user_data.get("last_event_check", 
                                                         current_time.isoformat()))
        
        # Check once per hour
        if (current_time - last_check).total_seconds() < 3600:
            return
        
        user_data["last_event_check"] = current_time.isoformat()
        
        # Check for penalty status to influence event chances
        has_active_penalty = any(task.get("type") == "penalty" 
                               for task in user_data["tasks"].get("penalty", {}).values())
        
        for event_name, event in self.events.items():
            base_chance = event["trigger_chance"]
            
            # Modify chances based on situation
            if has_active_penalty and event.get("type") == "recovery":
                base_chance *= 2  # Double chance for recovery events during penalties
            elif not has_active_penalty and event.get("type") == "positive":
                base_chance *= 1.5  # Increased chance for positive events when doing well
            
            if random.random() < base_chance:
                self.trigger_event(event_name, event, user_data)

    def trigger_event(self, event_name: str, event: dict, user_data: Dict):
        """Trigger a special event"""
        if "active_events" not in user_data:
            user_data["active_events"] = []
            
        # Add event to active events
        event_instance = {
            "name": event_name,
            **event,
            "start_time": datetime.now().isoformat(),
            "completed": False
        }
        
        user_data["active_events"].append(event_instance)
        
        # Apply immediate effects
        if event.get("type") == "positive":
            self.apply_positive_effects(event, user_data)
        
        # Show event notification
        self.show_event_notification(event_name, event)

    def show_event_notification(self, event_name: str, event: dict):
        """Display event notification"""
        st.markdown(f"""
            <div class="event-notification {event['rarity'].lower()} {event.get('type', '')}">
                <div class="event-icon">{event['icon']}</div>
                <div class="event-content">
                    <h3>{event_name}</h3>
                    <p>{event['description']}</p>
                    <p class="event-duration">Duration: {event['duration']} hours</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.balloons()

    def update_active_events(self, user_data: Dict):
        """Update and remove expired events"""
        if "active_events" not in user_data:
            return
        
        current_time = datetime.now()
        active_events = []
        
        for event in user_data["active_events"]:
            start_time = datetime.fromisoformat(event["start_time"])
            duration = timedelta(hours=event["duration"])
            
            if start_time + duration > current_time:
                active_events.append(event)
            else:
                # Handle event expiration
                if event.get("type") == "challenge":
                    self.handle_challenge_completion(event, user_data)
                self.remove_event_effects(event, user_data)
                
                # Add to event history
                if "event_history" not in user_data:
                    user_data["event_history"] = []
                event["completed_at"] = current_time.isoformat()
                user_data["event_history"].append(event)
        
        user_data["active_events"] = active_events

    def handle_challenge_completion(self, event: dict, user_data: Dict):
        """Handle challenge event completion"""
        if self.check_challenge_success(event, user_data):
            self.apply_success_reward(event["success_reward"], user_data)
            st.success(f"Challenge '{event['name']}' completed successfully!")
        else:
            self.apply_failure_penalty(event["failure_penalty"], user_data)
            st.warning(f"Challenge '{event['name']}' failed!")

    def check_challenge_success(self, event: dict, user_data: Dict) -> bool:
        """Check if challenge was completed successfully"""
        if event["name"] == "Perfect Day Challenge":
            return all(task.get("completed", False) for task in user_data["tasks"]["daily"].values())
        elif event["name"] == "Speed Runner Challenge":
            return self.check_speed_challenge(user_data)
        return False

    def check_speed_challenge(self, user_data: Dict) -> bool:
        """Check if speed runner challenge was completed"""
        daily_tasks = user_data["tasks"]["daily"]
        if not daily_tasks:
            return False
        
        completion_times = []
        for task in daily_tasks.values():
            if not task.get("completed", False):
                return False
            completion_times.append(datetime.fromisoformat(task["completed_at"]))
        
        time_range = max(completion_times) - min(completion_times)
        return time_range.total_seconds() <= 21600  # 6 hours in seconds

    def apply_positive_effects(self, event: dict, user_data: Dict):
        """Apply positive event effects"""
        effects = event.get("effects", {})
        
        if "point_multiplier" in effects:
            if "multipliers" not in user_data:
                user_data["multipliers"] = {}
            user_data["multipliers"]["event"] = effects["point_multiplier"]
        
        if "attribute_boost" in effects:
            if "attribute_multipliers" not in user_data:
                user_data["attribute_multipliers"] = {}
            attribute = random.choice(list(user_data["attributes"].keys()))
            user_data["attribute_multipliers"][attribute] = effects["attribute_boost"]
        
        if "all_attributes_boost" in effects:
            if "attribute_multipliers" not in user_data:
                user_data["attribute_multipliers"] = {}
            for attribute in user_data["attributes"]:
                user_data["attribute_multipliers"][attribute] = effects["all_attributes_boost"]
        
        if "streak_multiplier" in effects:
            if "multipliers" not in user_data:
                user_data["multipliers"] = {}
            user_data["multipliers"]["streak"] = effects["streak_multiplier"]

    def apply_success_reward(self, reward: dict, user_data: Dict):
        """Apply challenge success rewards"""
        if "all_attributes" in reward:
            for attr in user_data["attributes"]:
                user_data["attributes"][attr] += reward["all_attributes"]
        
        if "streak_bonus" in reward:
            user_data["streak"] += reward["streak_bonus"]
        
        if "point_multiplier" in reward:
            if "multipliers" not in user_data:
                user_data["multipliers"] = {}
            user_data["multipliers"]["event"] = reward["point_multiplier"]

    def apply_failure_penalty(self, penalty: dict, user_data: Dict):
        """Apply challenge failure penalties"""
        if "streak_reduction" in penalty:
            user_data["streak"] = max(0, user_data["streak"] - penalty["streak_reduction"])
        
        if "point_reduction" in penalty:
            for attr in user_data["attributes"]:
                user_data["attributes"][attr] = max(0, 
                    user_data["attributes"][attr] - penalty["point_reduction"]
                )

    def remove_event_effects(self, event: dict, user_data: Dict):
        """Remove event effects when expired"""
        if event.get("effects"):
            if "point_multiplier" in event["effects"]:
                user_data["multipliers"].pop("event", None)
            
            if "attribute_boost" in event["effects"] or "all_attributes_boost" in event["effects"]:
                user_data.pop("attribute_multipliers", None)
            
            if "streak_multiplier" in event["effects"]:
                user_data["multipliers"]["streak"] = 1.0