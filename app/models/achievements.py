# app/models/achievements.py
from typing import Dict, List
from datetime import datetime, timedelta
import streamlit as st

class AchievementSystem:
    def __init__(self):
        self.achievements = {
            # Task Achievements
            "first_step": {
                "id": "first_step",
                "name": "First Step",
                "description": "Complete your first task",
                "requirement": lambda user_data: self.check_tasks_completed(user_data, 1),
                "reward": {"all_attributes": 1},
                "icon": "🎯",
                "rarity": "Common"
            },
            "task_master": {
                "id": "task_master",
                "name": "Task Master",
                "description": "Complete 50 tasks",
                "requirement": lambda user_data: self.check_tasks_completed(user_data, 50),
                "reward": {"all_attributes": 2},
                "icon": "✨",
                "rarity": "Uncommon"
            },
            "centurion": {
                "id": "centurion",
                "name": "Centurion",
                "description": "Complete 100 tasks",
                "requirement": lambda user_data: self.check_tasks_completed(user_data, 100),
                "reward": {"all_attributes": 3},
                "icon": "💫",
                "rarity": "Rare"
            },
            # Streak Achievements
            "consistent": {
                "id": "consistent",
                "name": "Consistent",
                "description": "Maintain a 7-day streak",
                "requirement": lambda user_data: user_data.get("streak", 0) >= 7,
                "reward": {"streak_multiplier": 1.2},
                "icon": "🔥",
                "rarity": "Uncommon"
            },
            "unstoppable": {
                "id": "unstoppable",
                "name": "Unstoppable",
                "description": "Maintain a 30-day streak",
                "requirement": lambda user_data: user_data.get("streak", 0) >= 30,
                "reward": {"streak_multiplier": 1.5},
                "icon": "⚡",
                "rarity": "Rare"
            }
        }

    def check_achievements(self, user_data: Dict) -> List[Dict]:
        """Check for newly completed achievements"""
        if "completed_achievements" not in user_data:
            user_data["completed_achievements"] = []
            
        new_achievements = []
        completed_ids = user_data["completed_achievements"]
        
        for achievement_id, achievement in self.achievements.items():
            if (achievement_id not in completed_ids and 
                achievement["requirement"](user_data)):
                
                new_achievements.append(achievement)
                self.grant_achievement(achievement_id, achievement, user_data)
                self.show_achievement_notification(achievement)
        
        return new_achievements

    def grant_achievement(self, achievement_id: str, achievement: Dict, user_data: Dict):
        """Grant achievement and its rewards"""
        user_data["completed_achievements"].append(achievement_id)
        
        reward = achievement["reward"]
        if "all_attributes" in reward:
            for attr in user_data["attributes"]:
                user_data["attributes"][attr] += reward["all_attributes"]
        
        if "points" in reward:
            max_attr = max(user_data["attributes"].items(), key=lambda x: x[1])[0]
            user_data["attributes"][max_attr] += reward["points"]
        
        if "streak_multiplier" in reward:
            if "multipliers" not in user_data:
                user_data["multipliers"] = {}
            user_data["multipliers"]["streak"] = reward["streak_multiplier"]

    def show_achievement_notification(self, achievement: Dict):
        """Display achievement notification"""
        st.markdown(f"""
            <div class="achievement-notification {achievement['rarity'].lower()}">
                <div class="achievement-icon">{achievement['icon']}</div>
                <div class="achievement-content">
                    <h3>Achievement Unlocked!</h3>
                    <p class="achievement-name">{achievement['name']}</p>
                    <p class="achievement-description">{achievement['description']}</p>
                    <div class="achievement-reward">
                        <span class="reward-label">Reward:</span>
                        <span class="reward-value">{self.format_reward(achievement['reward'])}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()

    def get_available_achievements(self, user_data: Dict) -> List[Dict]:
        """Get list of available achievements"""
        completed_ids = user_data.get("completed_achievements", [])
        return [
            achievement for achievement_id, achievement in self.achievements.items()
            if achievement_id not in completed_ids
        ]

    def get_completed_achievements(self, user_data: Dict) -> List[Dict]:
        """Get list of completed achievements with details"""
        completed_ids = user_data.get("completed_achievements", [])
        return [
            self.achievements[achievement_id]
            for achievement_id in completed_ids
            if achievement_id in self.achievements
        ]

    def check_tasks_completed(self, user_data: Dict, count: int) -> bool:
        """Check if user has completed specified number of tasks"""
        total_completed = 0
        
        for task_type in ["daily", "weekly", "special"]:
            if task_type in user_data.get("tasks", {}):
                total_completed += sum(
                    1 for task in user_data["tasks"][task_type].values()
                    if task.get("completed", False)
                )
        
        return total_completed >= count

    @staticmethod
    def format_reward(reward: Dict) -> str:
        """Format reward for display"""
        if "all_attributes" in reward:
            return f"+{reward['all_attributes']} to all attributes"
        elif "points" in reward:
            return f"+{reward['points']} points"
        elif "streak_multiplier" in reward:
            return f"{reward['streak_multiplier']}x streak bonus"
        return str(reward)