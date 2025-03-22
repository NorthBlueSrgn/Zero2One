# app.py
import streamlit as st
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

# Import all components
from app.models.achievement_chains import AchievementSystem
from app.models.dynamic_events import SpecialEvents
from app.models.jobs import JobSystem
from app.models.tasks import TaskManager
from app.services.data_manager import DataManager
from app.services.progress_tracker import ProgressTracker

class Zero2OneApp:
    def __init__(self):
        self.data_manager = DataManager()
        self.task_manager = TaskManager()
        self.achievement_system = AchievementSystem()
        self.job_system = JobSystem()
        self.progress_tracker = ProgressTracker()
        self.special_events = SpecialEvents()

    def initialize(self):
        """Initialize the application"""
        # Load saved state
        self.data_manager.load_state()
        
        # Check and update events
        self.special_events.check_for_events(st.session_state.user_data)
        self.special_events.update_active_events(st.session_state.user_data)
        
        # Check for achievements
        new_achievements = self.achievement_system.check_achievements(st.session_state.user_data)
        
        # Auto-save state
        self.data_manager.save_state()

    def run(self):
        """Run the main application"""
        # Sidebar
        self.create_sidebar()
        
        # Main content
        if st.session_state.get("current_page") == "Dashboard":
            self.show_dashboard()
        elif st.session_state.get("current_page") == "Tasks":
            self.show_tasks()
        elif st.session_state.get("current_page") == "Jobs":
            self.show_jobs()
        elif st.session_state.get("current_page") == "Stats":
            self.show_stats()
        elif st.session_state.get("current_page") == "Settings":
            self.show_settings()

    def create_sidebar(self):
        """Create sidebar navigation"""
        with st.sidebar:
            st.markdown("""
                <div style="text-align: center; padding: 1rem;">
                    <h1 style="color: #8B5CF6;">ZERO2ONE</h1>
                    <p>Break your limits. Evolve. Become stronger.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            pages = {
                "Dashboard": "🏰",
                "Tasks": "📜",
                "Jobs": "💼",
                "Stats": "📊",
                "Settings": "⚙️"
            }
            
            for page, icon in pages.items():
                if st.button(
                    f"{icon} {page}",
                    key=f"nav_{page}",
                    use_container_width=True
                ):
                    st.session_state.current_page = page
                    st.experimental_rerun()
            
            # Show active events
            self.special_events.display_active_events(st.session_state.user_data)
            
            # Show streak
            st.markdown(f"""
                <div class="streak-container">
                    <h3>Current Streak</h3>
                    <div class="streak-number">{st.session_state.user_data['streak']} days</div>
                    <div class="streak-progress">
                        <div class="streak-bar" 
                             style="width: {(st.session_state.user_data['streak'] % 8) * 12.5}%">
                        </div>
                    </div>
                    <p>Next reward in {8 - (st.session_state.user_data['streak'] % 8)} days</p>
                </div>
            """, unsafe_allow_html=True)

    def show_dashboard(self):
        """Display dashboard page"""
        st.markdown("""
            <div class="dashboard-header">
                <h1>Your Journey</h1>
                <p>Track your progress from zero to one</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.progress_tracker.display_stats_page(st.session_state.user_data)
        
        with col2:
            self.special_events.display_active_events(st.session_state.user_data)
            if st.session_state.user_data.get("current_job"):
                self.job_system.display_current_job(st.session_state.user_data["current_job"])

    def show_tasks(self):
        self.task_manager.create_task_interface()
        self.task_manager.display_tasks()

    def show_jobs(self):
        self.job_system.display_jobs(st.session_state.user_data)

    def show_stats(self):
        self.progress_tracker.display_stats_page(st.session_state.user_data)

    def show_settings(self):
        self.data_manager.display_settings()

def load_css():
    """Load custom CSS"""
    with open('static/styles/main.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # Page config
    st.set_page_config(
        page_title="ZERO2ONE - Solo Leveling System",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load custom CSS
    load_css()

    # Load Google Fonts
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Initialize app
    if 'app' not in st.session_state:
        st.session_state.app = Zero2OneApp()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Initialize and run app
    st.session_state.app.initialize()
    st.session_state.app.run()

if __name__ == "__main__":
    main()
