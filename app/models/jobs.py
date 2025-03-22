from typing import Dict, List
import streamlit as st
from datetime import datetime

class JobSystem:
    def __init__(self):
        self.jobs = {
            # E Rank - Bottom Tier
            "Master of None": {
                "rank_requirement": "E",
                "attribute_requirements": {},
                "description": "One who has yet to find their path.",
                "perk": "No perks yet...",
                "perk_multiplier": 1.0,
                "tier": "low",
                "icon": "❓"
            },
            "Stray Dog": {
                "rank_requirement": "E",
                "attribute_requirements": {"resilience": 50},
                "description": "Surviving through instinct and determination.",
                "perk": "Resilience tasks give +10% more points.",
                "perk_multiplier": 1.1,
                "tier": "low",
                "icon": "🐕"
            },
            
            # D Rank - Low Tier
            "Pugilist": {
                "rank_requirement": "D",
                "attribute_requirements": {
                    "physical": 85,
                    "resilience": 50
                },
                "description": "Street fighter learning the ways of combat.",
                "perk": "Physical tasks give +15% more points.",
                "perk_multiplier": 1.15,
                "tier": "low",
                "icon": "🥊"
            },
            "Swindler": {
                "rank_requirement": "D",
                "attribute_requirements": {
                    "intelligence": 85,
                    "creativity": 50
                },
                "description": "Master of deception and quick wit.",
                "perk": "Intelligence tasks give +15% more points.",
                "perk_multiplier": 1.15,
                "tier": "low",
                "icon": "🎭"
            },
            "Apprentice": {
                "rank_requirement": "D",
                "attribute_requirements": {
                    "intelligence": 85
                },
                "description": "Beginning the path of knowledge.",
                "perk": "Learning tasks give +15% more points.",
                "perk_multiplier": 1.15,
                "tier": "low",
                "icon": "📚"
            },
            
            # C Rank - Mid Tier
            "Duelist": {
                "rank_requirement": "C",
                "attribute_requirements": {
                    "physical": 170,
                    "resilience": 85
                },
                "description": "Skilled fighter specializing in one-on-one combat.",
                "perk": "Combat tasks give +20% more points.",
                "perk_multiplier": 1.2,
                "tier": "mid",
                "icon": "⚔️"
            },
            "Phantom Jester": {
                "rank_requirement": "C",
                "attribute_requirements": {
                    "creativity": 170,
                    "spiritual": 85
                },
                "description": "Mystifying performer of the supernatural.",
                "perk": "Creative tasks give +20% more points.",
                "perk_multiplier": 1.2,
                "tier": "mid",
                "icon": "🃏"
            },
            "Marksman": {
                "rank_requirement": "C",
                "attribute_requirements": {
                    "physical": 170,
                    "intelligence": 85
                },
                "description": "Precision shooter with deadly accuracy.",
                "perk": "Precision tasks give +20% more points.",
                "perk_multiplier": 1.2,
                "tier": "mid",
                "icon": "🎯"
            },
            "Nomad": {
                "rank_requirement": "C",
                "attribute_requirements": {
                    "resilience": 170,
                    "spiritual": 85
                },
                "description": "Wandering soul seeking truth.",
                "perk": "Exploration tasks give +20% more points.",
                "perk_multiplier": 1.2,
                "tier": "mid",
                "icon": "🌎"
            },
            "Shaman": {
                "rank_requirement": "C",
                "attribute_requirements": {
                    "spiritual": 170,
                    "intelligence": 85
                },
                "description": "Speaker to spirits and natural forces.",
                "perk": "Spiritual tasks give +25% more points.",
                "perk_multiplier": 1.25,
                "tier": "mid",
                "icon": "🕯️"
            },
            
            # B Rank - Advanced Tier
            "Iron Sentinel": {
                "rank_requirement": "B",
                "attribute_requirements": {
                    "physical": 255,
                    "resilience": 170
                },
                "description": "Unbreakable guardian of order.",
                "perk": "Defense tasks give +30% more points.",
                "perk_multiplier": 1.3,
                "tier": "advanced",
                "icon": "🛡️"
            },
            "Shade Operative": {
                "rank_requirement": "B",
                "attribute_requirements": {
                    "intelligence": 255,
                    "physical": 170
                },
                "description": "Elite agent working in the shadows.",
                "perk": "Stealth tasks give +30% more points.",
                "perk_multiplier": 1.3,
                "tier": "advanced",
                "icon": "🕴️"
            },
            "Revenant": {
                "rank_requirement": "B",
                "attribute_requirements": {
                    "spiritual": 255,
                    "resilience": 170
                },
                "description": "One who has returned from the brink.",
                "perk": "Recovery tasks give +30% more points.",
                "perk_multiplier": 1.3,
                "tier": "advanced",
                "icon": "👻"
            },
            "Battle Hound": {
                "rank_requirement": "B",
                "attribute_requirements": {
                    "physical": 255,
                    "spiritual": 170
                },
                "description": "Warrior with bestial instincts.",
                "perk": "Combat tasks give +35% more points.",
                "perk_multiplier": 1.35,
                "tier": "advanced",
                "icon": "🐺"
            },
            
            # A Rank - Elite Tier
            "Order Member": {
                "rank_requirement": "A",
                "attribute_requirements": {
                    "intelligence": 340,
                    "spiritual": 255,
                    "resilience": 170
                },
                "description": "Elite member of a secret organization.",
                "perk": "All attributes gain +40% more points.",
                "perk_multiplier": 1.4,
                "tier": "elite",
                "icon": "⭐"
            },
            "Elite Assassin": {
                "rank_requirement": "A",
                "attribute_requirements": {
                    "physical": 340,
                    "intelligence": 255,
                    "resilience": 170
                },
                "description": "Master of the deadly arts.",
                "perk": "Assassination tasks give +45% more points.",
                "perk_multiplier": 1.45,
                "tier": "elite",
                "icon": "🗡️"
            },
            "Shadow Puppeteer": {
                "rank_requirement": "A",
                "attribute_requirements": {
                    "creativity": 340,
                    "spiritual": 255,
                    "intelligence": 170
                },
                "description": "Master manipulator of shadows and minds.",
                "perk": "Control tasks give +45% more points.",
                "perk_multiplier": 1.45,
                "tier": "elite",
                "icon": "🎭"
            },
            
            # S Rank - Legendary
            "The Glitch": {
                "rank_requirement": "S",
                "attribute_requirements": {
                    "intelligence": 425,
                    "creativity": 425,
                    "spiritual": 340
                },
                "description": "One who has transcended normal limitations.",
                "perk": "All tasks give +50% more points.",
                "perk_multiplier": 1.5,
                "tier": "special",
                "icon": "🌟"
            },
            "Enigma": {
                "rank_requirement": "S",
                "attribute_requirements": {
                    "spiritual": 425,
                    "intelligence": 425,
                    "resilience": 340,
                    "creativity": 340
                },
                "description": "A being of infinite possibilities.",
                "perk": "All attributes gain +60% more points.",
                "perk_multiplier": 1.6,
                "tier": "special",
                "icon": "✨"
            }
        }
        
        self.tiers = {
            "low": "Low-Tier Jobs (E-D Rank)",
            "mid": "Mid-Tier Jobs (C Rank)",
            "advanced": "Advanced Jobs (B Rank)",
            "elite": "Elite Jobs (A Rank)",
            "special": "Special Jobs (S Rank)"
        }

    def display_jobs(self, user_data: Dict):
        """Display available jobs and current job status"""
        try:
            st.title("Career Progression")
            
            current_job = user_data.get("current_job")
            if current_job:
                self.display_current_job(current_job)
            
            available_jobs = self.get_available_jobs(user_data)
            
            for tier, tier_name in self.tiers.items():
                with st.expander(tier_name):
                    tier_jobs = [(name, job) for name, job in self.jobs.items() 
                               if job["tier"] == tier]
                    
                    if not tier_jobs:
                        st.info(f"No {tier_name} available yet.")
                        continue
                        
                    for job_name, job in tier_jobs:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(f"{job['icon']} {job_name}")
                            st.write(job['description'])
                            st.write(f"**Perk:** {job['perk']}")
                            if job['attribute_requirements']:
                                st.write("**Requirements:**")
                                for attr, val in job['attribute_requirements'].items():
                                    st.write(f"- {attr.title()}: {val}+")
                        with col2:
                            if job_name in available_jobs and job_name != current_job:
                                if st.button("Accept", key=f"accept_{job_name}"):
                                    self.accept_job(job_name, user_data)
                        st.divider()
                        
        except Exception as e:
            st.error(f"Error displaying jobs: {str(e)}")

    def display_current_job(self, job_name: str):
        """Display current job details"""
        try:
            if job_name not in self.jobs:
                return
                
            job = self.jobs[job_name]
            st.info(
                f"**Current Position:** {job['icon']} {job_name}\n\n"
                f"{job['description']}\n\n"
                f"**Active Perk:** {job['perk']}"
            )
            
        except Exception as e:
            st.error(f"Error displaying current job: {str(e)}")

    def get_available_jobs(self, user_data: Dict) -> List[str]:
        """Get list of jobs available to the user"""
        try:
            return [
                job_name for job_name, job in self.jobs.items()
                if self.check_job_requirements(job, user_data)
            ]
        except Exception as e:
            st.error(f"Error getting available jobs: {str(e)}")
            return []

    def check_job_requirements(self, job: Dict, user_data: Dict) -> bool:
        """Check if user meets job requirements"""
        try:
            return all(
                user_data["attributes"].get(attr, 0) >= required_value
                for attr, required_value in job["attribute_requirements"].items()
            )
        except Exception as e:
            st.error(f"Error checking job requirements: {str(e)}")
            return False

    def accept_job(self, job_name: str, user_data: Dict):
        """Accept a new job"""
        try:
            # Update current job
            user_data["current_job"] = job_name
            
            # Add to job history
            if "job_history" not in user_data:
                user_data["job_history"] = []
                
            user_data["job_history"].append({
                "job": job_name,
                "accepted_at": datetime.now().isoformat()
            })
            
            # Update job multiplier
            job = self.jobs[job_name]
            user_data["multipliers"]["job"] = job["perk_multiplier"]
            
            # Save state
            if 'data_manager' in st.session_state:
                st.session_state.data_manager.save_state()
            
            st.success(f"Congratulations! You are now a {job_name}!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error accepting job: {str(e)}")
