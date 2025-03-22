# app/models/achievement_chains.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st

class AchievementChain:
    def __init__(self, chain_id: str, name: str, description: str, 
                 stages: List[Dict], icon: str, rarity: str):
        self.chain_id = chain_id
        self.name = name
        self.description = description
        self.stages = stages
        self.icon = icon
        self.rarity = rarity
        self.current_stage = 0
        self.completed = False
        self.started_at = None
        self.completed_at = None

    def to_dict(self) -> Dict:
        return {
            "chain_id": self.chain_id,
            "name": self.name,
            "description": self.description,
            "stages": self.stages,
            "icon": self.icon,
            "rarity": self.rarity,
            "current_stage": self.current_stage,
            "completed": self.completed,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }

class AchievementChainSystem:
    def __init__(self):
        self.chains = {
            "physical_mastery": {
                "name": "Physical Mastery",
                "description": "Master your physical capabilities",
                "icon": "💪",
                "rarity": "Legendary",
                "stages": [
                    {
                        "name": "Beginner Athlete",
                        "requirement": lambda user_data: user_data["attributes"]["Physical"] >= 100,
                        "reward": {"Physical": 10},
                        "description": "Reach 100 Physical points"
                    },
                    {
                        "name": "Intermediate Athlete",
                        "requirement": lambda user_data: user_data["attributes"]["Physical"] >= 250,
                        "reward": {"Physical": 25, "Health": 10},
                        "description": "Reach 250 Physical points"
                    },
                    {
                        "name": "Advanced Athlete",
                        "requirement": lambda user_data: user_data["attributes"]["Physical"] >= 500,
                        "reward": {"all_attributes": 20},
                        "description": "Reach 500 Physical points"
                    }
                ]
            },
            "mind_master": {
                "name": "Mind Master",
                "description": "Develop your mental capabilities",
                "icon": "🧠",
                "rarity": "Epic",
                "stages": [
                    {
                        "name": "Knowledge Seeker",
                        "requirement": lambda user_data: user_data["attributes"]["Intelligence"] >= 100,
                        "reward": {"Intelligence": 10},
                        "description": "Reach 100 Intelligence points"
                    },
                    {
                        "name": "Scholar",
                        "requirement": lambda user_data: (
                            user_data["attributes"]["Intelligence"] >= 200 and
                            user_data["attributes"]["Creativity"] >= 100
                        ),
                        "reward": {"Intelligence": 20, "Creativity": 10},
                        "description": "Reach 200 Intelligence and 100 Creativity points"
                    },
                    {
                        "name": "Sage",
                        "requirement": lambda user_data: (
                            user_data["attributes"]["Intelligence"] >= 400 and
                            user_data["attributes"]["Creativity"] >= 200 and
                            user_data["attributes"]["Spiritual"] >= 100
                        ),
                        "reward": {"all_attributes": 25},
                        "description": "Master multiple mental attributes"
                    }
                ]
            },
            "consistency_king": {
                "name": "Consistency King",
                "description": "Master the art of consistency",
                "icon": "👑",
                "rarity": "Mythical",
                "stages": [
                    {
                        "name": "Habit Former",
                        "requirement": lambda user_data: user_data["streak"] >= 7,
                        "reward": {"streak_multiplier": 1.1},
                        "description": "Maintain a 7-day streak"
                    },
                    {
                        "name": "Routine Master",
                        "requirement": lambda user_data: (
                            user_data["streak"] >= 30 and
                            self.check_task_completion_rate(user_data, 0.8)
                        ),
                        "reward": {"streak_multiplier": 1.2},
                        "description": "30-day streak with 80% task completion"
                    },
                    {
                        "name": "Living Legend",
                        "requirement": lambda user_data: (
                            user_data["streak"] >= 100 and
                            self.check_task_completion_rate(user_data, 0.9)
                        ),
                        "reward": {"streak_multiplier": 1.5, "all_attributes": 50},
                        "description": "100-day streak with 90% task completion"
                    }
                ]
            }
        }
        self.load_chain_progress()

    def load_chain_progress(self):
        """Load achievement chain progress"""
        if 'achievement_chains' not in st.session_state:
            st.session_state.achievement_chains = {
                chain_id: AchievementChain(
                    chain_id=chain_id,
                    **chain_data
                ) for chain_id, chain_data in self.chains.items()
            }

    def check_chains(self, user_data: Dict):
        """Check progress on all achievement chains"""
        for chain_id, chain in st.session_state.achievement_chains.items():
            if not chain.completed:
                self.check_chain_progress(chain, user_data)

    def check_chain_progress(self, chain: AchievementChain, user_data: Dict):
        """Check progress on a specific achievement chain"""
        if not chain.started_at:
            chain.started_at = datetime.now().isoformat()

        current_stage = chain.stages[chain.current_stage]
        if current_stage["requirement"](user_data):
            # Grant stage rewards
            self.grant_stage_rewards(current_stage["reward"], user_data)
            
            # Update chain progress
            chain.current_stage += 1
            
            # Show notification
            self.show_stage_completion_notification(chain, current_stage)
            
            # Check if chain is completed
            if chain.current_stage >= len(chain.stages):
                chain.completed = True
                chain.completed_at = datetime.now().isoformat()
                self.show_chain_completion_notification(chain)

    def grant_stage_rewards(self, rewards: Dict, user_data: Dict):
        """Grant rewards for completing an achievement chain stage"""
        if "all_attributes" in rewards:
            for attr in user_data["attributes"]:
                user_data["attributes"][attr] += rewards["all_attributes"]
        else:
            for attr, value in rewards.items():
                if attr in user_data["attributes"]:
                    user_data["attributes"][attr] += value
                elif attr == "streak_multiplier":
                    if "multipliers" not in user_data:
                        user_data["multipliers"] = {}
                    user_data["multipliers"]["streak"] = value

    def show_stage_completion_notification(self, chain: AchievementChain, stage: Dict):
        """Show notification for stage completion"""
        st.markdown(f"""
            <div class="achievement-notification {chain.rarity.lower()}">
                <div class="achievement-icon">{chain.icon}</div>
                <div class="achievement-content">
                    <h3>{chain.name} - Stage {chain.current_stage}</h3>
                    <p>{stage['name']}</p>
                    <div class="achievement-reward">
                        Reward: {self.format_rewards(stage['reward'])}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()

    def show_chain_completion_notification(self, chain: AchievementChain):
        """Show notification for completing entire chain"""
        st.markdown(f"""
            <div class="achievement-notification {chain.rarity.lower()} chain-complete">
                <div class="achievement-icon">{chain.icon}</div>
                <div class="achievement-content">
                    <h3>Achievement Chain Completed!</h3>
                    <p>{chain.name}</p>
                    <p>{chain.description}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.snow()

    def display_chains(self):
        """Display achievement chains and progress"""
        st.markdown("### Achievement Chains")

        for chain_id, chain in st.session_state.achievement_chains.items():
            self.display_chain_card(chain)

    def display_chain_card(self, chain: AchievementChain):
        """Display individual achievement chain card"""
        progress = (chain.current_stage / len(chain.stages)) * 100 if not chain.completed else 100

        st.markdown(f"""
            <div class="chain-card {chain.rarity.lower()} {'completed' if chain.completed else ''}">
                <div class="chain-header">
                    <span class="chain-icon">{chain.icon}</span>
                    <h3>{chain.name}</h3>
                    <span class="chain-rarity">{chain.rarity}</span>
                </div>
                <p>{chain.description}</p>
                <div class="chain-progress">
                    <div class="progress-bar" style="width: {progress}%"></div>
                    <span class="progress-text">{progress:.0f}%</span>
                </div>
                <div class="chain-stages">
                    {self.format_stages(chain)}
                </div>
            </div>
        """, unsafe_allow_html=True)

    def format_stages(self, chain: AchievementChain) -> str:
        """Format stages for display"""
        stages_html = ""
        for i, stage in enumerate(chain.stages):
            status = "completed" if i < chain.current_stage else "current" if i == chain.current_stage else "locked"
            stages_html += f"""
                <div class="chain-stage {status}">
                    <h4>{stage['name']}</h4>
                    <p>{stage['description']}</p>
                    <div class="stage-reward">
                        Reward: {self.format_rewards(stage['reward'])}
                    </div>
                </div>
            """
        return stages_html

    @staticmethod
    def check_task_completion_rate(user_data: Dict, required_rate: float) -> bool:
        """Check if user maintains required task completion rate"""
        total_tasks = 0
        completed_tasks = 0
        
        for task_type in ["daily", "weekly"]:
            for task in user_data["tasks"][task_type].values():
                total_tasks += 1
                if task.get("completed", False):
                    completed_tasks += 1
        
        return (completed_tasks / total_tasks) >= required_rate if total_tasks > 0 else False

    @staticmethod
    def format_rewards(rewards: Dict) -> str:
        """Format rewards for display"""
        reward_texts = []
        for key, value in rewards.items():
            if key == "all_attributes":
                reward_texts.append(f"+{value} to all attributes")
            elif key == "streak_multiplier":
                reward_texts.append(f"{value}x streak multiplier")
            else:
                reward_texts.append(f"+{value} {key}")
        return ", ".join(reward_texts)