# app.py
import streamlit as st
from datetime import datetime, timedelta
import json
import os
import traceback
from typing import Dict, List, Optional
import plotly.graph_objects as go
import random

from app.models import (
    AchievementSystem,
    AchievementChainSystem,
    SpecialEvents,
    TaskManager,
    JobSystem,
    TaskTemplateManager,
    DynamicEventGenerator
)
from app.services.data_manager import DataManager
from app.services.progress_tracker import ProgressTracker
from app.services.analytics_dashboard import AnalyticsDashboard

class Zero2OneApp:
    def __init__(self):
        try:
            self.data_manager = DataManager()
            self.task_manager = TaskManager()
            self.achievement_system = AchievementSystem()
            self.job_system = JobSystem()
            self.special_events = SpecialEvents()
            self.progress_tracker = ProgressTracker()
            self.analytics_dashboard = AnalyticsDashboard()
            self.task_template_manager = TaskTemplateManager()
            self.achievement_chain_system = AchievementChainSystem()
            self.dynamic_event_generator = DynamicEventGenerator()
            
            st.session_state.data_manager = self.data_manager
            
        except Exception as e:
            st.error(f"Error initializing app components: {str(e)}")
            st.error(traceback.format_exc())
            raise

    def initialize(self):
        """Initialize the application state"""
        try:
            # Initialize user data if not exists
            if 'user_data' not in st.session_state:
                st.session_state.user_data = {
                    "attributes": {
                        "Health": 0,
                        "Physical": 0,
                        "Intelligence": 0,
                        "Spiritual": 0,
                        "Creativity": 0,
                        "Resilience": 0
                    },
                    "streak": 0,
                    "last_active": datetime.now().isoformat(),
                    "completed_achievements": [],
                    "job": None,
                    "job_history": [],
                    "active_events": [],
                    "event_history": [],
                    "last_event_check": datetime.now().isoformat(),
                    "multipliers": {
                        "streak": 1.0,
                        "event": 1.0,
                        "job": 1.0
                    },
                    "stats": {
                        "total_points_earned": 0,
                        "tasks_completed": 0,
                        "max_streak": 0,
                        "achievements_unlocked": 0
                    },
                    "daily_stats": {},
                    "weekly_stats": {},
                    "penalty_history": [],
                    "locked_attributes": {}
                }

            # Initialize tasks if not exists
            if 'tasks' not in st.session_state:
                st.session_state.tasks = {
                    "daily": {},
                    "weekly": {},
                    "special": {}
                }
            else:
                # Ensure all task types exist
                for task_type in ["daily", "weekly", "special"]:
                    if task_type not in st.session_state.tasks:
                        st.session_state.tasks[task_type] = {}

            # Initialize other components
            if 'custom_templates' not in st.session_state:
                st.session_state.custom_templates = {}
            
            if 'achievement_chains' not in st.session_state:
                st.session_state.achievement_chains = {}
            
            if 'active_events' not in st.session_state:
                st.session_state.active_events = []

            # Initialize task types in TaskManager
            self.task_manager.task_types = {
                "daily": "🌅 Daily Tasks",
                "weekly": "📅 Weekly Tasks",
                "special": "⭐ Special Tasks"
            }

            # Load saved state
            self.data_manager.load_state()
            
            # Update components
            self.task_manager.update_tasks(st.session_state.user_data)
            self.special_events.check_for_events(st.session_state.user_data)
            self.special_events.update_active_events(st.session_state.user_data)
            self.achievement_system.check_achievements(st.session_state.user_data)
            
            # Check for new events
            self.check_for_new_events()
            
            # Update achievement chains
            self.achievement_chain_system.check_chains(st.session_state.user_data)
            
            # Save state
            self.data_manager.save_state()

            # Verify task types are properly initialized
            for task_type in ["daily", "weekly", "special"]:
                if task_type not in st.session_state.tasks:
                    st.session_state.tasks[task_type] = {}
                    st.warning(f"Initialized missing task type: {task_type}")

        except Exception as e:
            st.error(f"Error during initialization: {str(e)}")
            st.error(traceback.format_exc())

    def check_for_new_events(self):
        current_time = datetime.now()
        last_check = datetime.fromisoformat(
            st.session_state.user_data.get("last_event_check", 
            current_time.isoformat())
        )
        
        if (current_time - last_check).total_seconds() >= 3600:
            if random.random() < 0.3:  # 30% chance for new event
                new_event = self.dynamic_event_generator.generate_event(
                    st.session_state.user_data
                )
                st.session_state.active_events.append(new_event)
            
            st.session_state.user_data["last_event_check"] = current_time.isoformat()

    def create_sidebar(self):
        with st.sidebar:
            st.markdown("""
                <div class="sidebar-header">
                    <h1>ZerO2One</h1>
                    <p> Welcome player to the system.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            pages = {
                "Dashboard": "🏰",
                "Tasks": "📜",
                "Templates": "📋",
                "Jobs": "💼",
                "Achievements": "🏆",
                "Events": "⚡",
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
            
            # Stats Overview
            streak = st.session_state.user_data.get("streak", 0)
            total_points = sum(st.session_state.user_data["attributes"].values())
            current_rank, next_rank, progress = self.progress_tracker.calculate_rank(total_points)
            
            st.markdown(f"""
                <div class="sidebar-stats">
                    <div class="stat-item">
                        <span class="stat-label">Streak</span>
                        <span class="stat-value">{streak} days</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Rank</span>
                        <span class="stat-value">{current_rank}</span>
                    </div>
                </div>
                <div class="rank-progress">
                    <div class="progress-bar" style="width: {progress*100}%"></div>
                    <span class="progress-text">Progress to {next_rank}</span>
                </div>
            """, unsafe_allow_html=True)

            # Attributes
            st.markdown("<h3>Attributes</h3>", unsafe_allow_html=True)
            for attr, value in st.session_state.user_data["attributes"].items():
                current_rank, _, _ = self.progress_tracker.calculate_rank(value)
                st.markdown(f"""
                    <div class="attribute-item">
                        <span class="attribute-name">{attr}</span>
                        <span class="attribute-value">{value}</span>
                        <span class="attribute-rank">Rank {current_rank}</span>
                    </div>
                """, unsafe_allow_html=True)

            # Active Events Preview
            active_events = st.session_state.active_events
            if active_events:
                st.markdown("<h3>Active Events</h3>", unsafe_allow_html=True)
                for event in active_events[:2]:
                    st.markdown(f"""
                        <div class="event-preview {event['rarity'].lower()}">
                            <span class="event-icon">{event['icon']}</span>
                            <span class="event-name">{event['name']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                if len(active_events) > 2:
                    st.markdown(f"+{len(active_events) - 2} more events")

    def create_radar_chart(self, attributes: dict) -> go.Figure:
        """Create radar chart based on rank values with color gradient background"""
        rank_values = {
            "E": 1, "D": 2, "C": 3, "B": 4,
            "A": 5, "S": 6, "SS": 7, "SSS": 8
        }
        
        values = []
        for attr_value in attributes.values():
            current_rank, _, _ = self.progress_tracker.calculate_rank(attr_value)
            values.append(rank_values.get(current_rank, 0))
        
        values.append(values[0])
        categories = list(attributes.keys())
        categories.append(categories[0])

        fig = go.Figure()

        # Create gradient background with color transition
        num_circles = 32  # More circles for smoother gradient
        for i in range(num_circles, 0, -1):
            ratio = i / num_circles
            opacity = 0.15  # Consistent opacity
            radius = 8 * ratio
            
            # Color transition from red -> orange -> yellow -> green
            if ratio < 0.25:  # Red zone (center)
                color = f'rgba(255, 0, 0, {opacity})'
            elif ratio < 0.5:  # Orange zone
                color = f'rgba(255, 165, 0, {opacity})'
            elif ratio < 0.75:  # Yellow zone
                color = f'rgba(255, 255, 0, {opacity})'
            else:  # Green zone (outer)
                color = f'rgba(0, 255, 0, {opacity})'
            
            fig.add_trace(go.Scatterpolar(
                r=[radius] * len(categories),
                theta=categories,
                mode='lines',
                fill='toself',
                fillcolor=color,
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))

        # Add main data trace
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(255, 255, 255, 0.1)',
            line=dict(color='white', width=2),
            hovertemplate="<b>%{theta}</b><br>" +
                        "Points: " + str(list(attributes.values())) + "<extra></extra>"
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 8],
                    showticklabels=False,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    linecolor='rgba(255, 255, 255, 0.2)',
                ),
                angularaxis=dict(
                    showline=True,
                    linecolor='rgba(255, 255, 255, 0.8)',
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    color='white'
                ),
                bgcolor='rgba(0, 0, 0, 0)'
            ),
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=False
        )
        
        return fig
    

    def show_attributes_section(self):
        """Display attributes in a 2x3 grid"""
        attributes = list(st.session_state.user_data["attributes"].items())
        mid_point = len(attributes) // 2
        
        # First row
        cols = st.columns(3)
        for i, (attr, value) in enumerate(attributes[:3]):
            with cols[i]:
                current_rank, next_rank, progress = self.progress_tracker.calculate_rank(value)
                st.markdown(f"""
                    <div class="attribute-card">
                        <div class="attribute-header">
                            <span class="attribute-name">{attr}</span>
                            <span class="attribute-value">{value}</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {progress*100}%"></div>
                        </div>
                        <div class="progress-details">
                            <span>Rank {current_rank} → {next_rank}</span>
                            <span>{int(progress*100)}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Second row
        cols = st.columns(3)
        for i, (attr, value) in enumerate(attributes[3:]):
            with cols[i]:
                current_rank, next_rank, progress = self.progress_tracker.calculate_rank(value)
                st.markdown(f"""
                    <div class="attribute-card">
                        <div class="attribute-header">
                            <span class="attribute-name">{attr}</span>
                            <span class="attribute-value">{value}</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {progress*100}%"></div>
                        </div>
                        <div class="progress-details">
                            <span>Rank {current_rank} → {next_rank}</span>
                            <span>{int(progress*100)}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    def run(self):
        try:
            self.create_sidebar()
            
            current_page = st.session_state.get("current_page", "Dashboard")
            
            if current_page == "Dashboard":
                self.show_dashboard()
            elif current_page == "Tasks":
                self.show_tasks()
            elif current_page == "Templates":
                self.show_templates()
            elif current_page == "Jobs":
                self.show_jobs()
            elif current_page == "Achievements":
                self.show_achievements()
            elif current_page == "Events":
                self.show_events()
            elif current_page == "Stats":
                self.show_stats()
            elif current_page == "Settings":
                self.show_settings()

        except Exception as e:
            st.error(f"Error in main app loop: {str(e)}")
            st.error(traceback.format_exc())

    def show_dashboard(self):
        
        try:
            # Header and Quote
            st.markdown("""
                <div class="dashboard-header">
                    <h1>ZERO2ONE</h1>
                    <div class="quote-container">
                        <p class="quote-text">
                            "You don't rise to the level of your goals, you fall to the level of your systems. 
                            Break yourself down as many times as necessary until you turn zero to one."
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            

            # Main Stats Row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                    <div class="stat-card">
                        <h3>Total Points</h3>
                        <div class="stat-value">{}</div>
                    </div>
                """.format(sum(st.session_state.user_data["attributes"].values())), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="stat-card">
                        <h3>Current Streak</h3>
                        <div class="stat-value">{} days</div>
                    </div>
                """.format(st.session_state.user_data['streak']), unsafe_allow_html=True)
            
            with col3:
                completed_tasks = sum(1 for tasks in st.session_state.tasks.values() 
                                for task in tasks.values() if task.get("completed", False))
                st.markdown("""
                    <div class="stat-card">
                        <h3>Tasks Completed</h3>
                        <div class="stat-value">{}</div>
                    </div>
                """.format(completed_tasks), unsafe_allow_html=True)

            # Attributes and Radar Chart
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown("<h2>Attributes</h2>", unsafe_allow_html=True)
                
                # First row of attributes
                cols_row1 = st.columns(3)
                attributes = list(st.session_state.user_data["attributes"].items())
                
                # Display first three attributes
                for i, (attr, value) in enumerate(attributes[:3]):
                    with cols_row1[i]:
                        current_rank, next_rank, progress = self.progress_tracker.calculate_rank(value)
                        st.markdown(f"""
                            <div class="attribute-card">
                                <div class="attribute-header">
                                    <span class="attribute-name">{attr}</span>
                                    <span class="attribute-value">{value}</span>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-bar" style="width: {progress*100}%"></div>
                                </div>
                                <div class="progress-details">
                                    <span>Rank {current_rank} → {next_rank}</span>
                                    <span>{int(progress*100)}%</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Second row of attributes
                cols_row2 = st.columns(3)
                
                # Display last three attributes
                for i, (attr, value) in enumerate(attributes[3:]):
                    with cols_row2[i]:
                        current_rank, next_rank, progress = self.progress_tracker.calculate_rank(value)
                        st.markdown(f"""
                            <div class="attribute-card">
                                <div class="attribute-header">
                                    <span class="attribute-name">{attr}</span>
                                    <span class="attribute-value">{value}</span>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-bar" style="width: {progress*100}%"></div>
                                </div>
                                <div class="progress-details">
                                    <span>Rank {current_rank} → {next_rank}</span>
                                    <span>{int(progress*100)}%</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                

            with col2:
                st.plotly_chart(
                    self.create_radar_chart(st.session_state.user_data["attributes"]), 
                    use_container_width=True
                )

            # Active Events
            if st.session_state.active_events:
                st.markdown("<h2>Active Events</h2>", unsafe_allow_html=True)
                event_cols = st.columns(2)
                for idx, event in enumerate(st.session_state.active_events):
                    with event_cols[idx % 2]:
                        start_time = datetime.fromisoformat(event['start_time'])
                        time_left = start_time + timedelta(hours=event['duration']) - datetime.now()
                        
                        st.markdown(f"""
                            <div class="event-card {event['rarity'].lower()}">
                                <div class="event-header">
                                    <span class="event-icon">{event['icon']}</span>
                                    <h3>{event['name']}</h3>
                                    <span class="event-rarity">{event['rarity']}</span>
                                </div>
                                <p class="event-description">{event['description']}</p>
                                <div class="event-timer">Time remaining: {str(time_left).split('.')[0]}</div>
                            </div>
                        """, unsafe_allow_html=True)

            # Today's Tasks
            st.markdown("<h2>Today's Tasks</h2>", unsafe_allow_html=True)
            daily_tasks = st.session_state.tasks["daily"]
            if daily_tasks:
                # Task Progress
                completed = sum(1 for task in daily_tasks.values() if task.get("completed", False))
                total = len(daily_tasks)
                
                st.markdown(f"""
                    <div class="tasks-progress">
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {(completed/total*100) if total > 0 else 0}%"></div>
                        </div>
                        <div class="progress-label">
                            <span>Completed: {completed}/{total} tasks</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Active Tasks Display
                task_cols = st.columns(2)
                active_tasks = [task for task in daily_tasks.values() if not task.get("completed", False)]
                
                for idx, task in enumerate(active_tasks):
                    with task_cols[idx % 2]:
                        st.markdown(f"""
                            <div class="task-card">
                                <div class="task-header">
                                    <h3>{task['name']}</h3>
                                    <span class="task-points">+{task['points']} {task['attribute']}</span>
                                </div>
                                {f'<p class="task-description">{task["description"]}</p>' if task.get('description') else ''}
                            </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Complete", key=f"complete_{task['id']}"):
                                self.task_manager.complete_task(task['id'], task, "daily")
                        with col2:
                            if st.button("Remove", key=f"remove_{task['id']}"):
                                self.task_manager.remove_task(task['id'], "daily")
            else:
                st.info("No tasks for today. Create some tasks to begin your journey!")

        except Exception as e:
            st.error(f"Error displaying dashboard: {str(e)}")
            st.error(traceback.format_exc())

    def show_tasks(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Tasks</h1>
                    <p class="subtitle">Manage your daily journey</p>
                </div>
            """, unsafe_allow_html=True)

            # Create Task Section
            with st.expander("Create New Task", expanded=True):
                self.task_manager.create_task_interface()

            # Task Lists
            tabs = st.tabs(["Daily Tasks", "Weekly Tasks", "Special Tasks"])
            
            for i, task_type in enumerate(["daily", "weekly", "special"]):
                with tabs[i]:
                    tasks = st.session_state.tasks.get(task_type, {})
                    if not tasks:
                        st.info(f"No {task_type} tasks yet. Create some tasks to begin!")
                        continue

                    # Progress bar
                    completed = sum(1 for task in tasks.values() if task.get("completed", False))
                    total = len(tasks)
                    st.markdown(f"""
                        <div class="tasks-progress">
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {(completed/total*100)}%"></div>
                            </div>
                            <div class="progress-label">
                                <span>Completed: {completed}/{total}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Active tasks
                    for task_id, task in tasks.items():
                        if not task.get("completed", False):
                            st.markdown(f"""
                                <div class="task-card">
                                    <div class="task-header">
                                        <span class="task-name">{task['name']}</span>
                                        <span class="task-points">+{task['points']} {task['attribute']}</span>
                                    </div>
                                    {f'<p class="task-description">{task["description"]}</p>' if task.get('description') else ''}
                                </div>
                            """, unsafe_allow_html=True)

                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("Complete", key=f"complete_{task_id}"):
                                    self.task_manager.complete_task(task_id, task, task_type)
                            with col2:
                                if st.button("Remove", key=f"remove_{task_id}"):
                                    self.task_manager.remove_task(task_id, task_type)

        except Exception as e:
            st.error(f"Error displaying tasks: {str(e)}")

    def show_templates(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Task Templates</h1>
                    <p class="subtitle">Create and manage task templates</p>
                </div>
            """, unsafe_allow_html=True)

            tabs = st.tabs(["Create Template", "Browse Templates"])
            
            with tabs[0]:
                self.task_template_manager.create_template_interface()
            
            with tabs[1]:
                self.task_template_manager.display_templates()

        except Exception as e:
            st.error(f"Error displaying templates: {str(e)}")

    def show_jobs(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Jobs</h1>
                    <p class="subtitle">Career progression and opportunities</p>
                </div>
            """, unsafe_allow_html=True)

            self.job_system.display_jobs(st.session_state.user_data)

        except Exception as e:
            st.error(f"Error displaying jobs: {str(e)}")

    def show_achievements(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Achievements</h1>
                    <p>Your journey to greatness</p>
                </div>
            """, unsafe_allow_html=True)

            tabs = st.tabs(["Available", "Completed"])
            
            with tabs[0]:
                available = self.achievement_system.get_available_achievements(st.session_state.user_data)
                if available:
                    for achievement in available:
                        st.markdown(f"""
                            <div class="achievement-card {achievement['rarity'].lower()}">
                                <div class="achievement-header">
                                    <span class="achievement-icon">{achievement['icon']}</span>
                                    <h3>{achievement['name']}</h3>
                                    <span class="achievement-rarity">{achievement['rarity']}</span>
                                </div>
                                <p class="achievement-description">{achievement['description']}</p>
                                <div class="achievement-reward">
                                    <span class="reward-label">Reward:</span>
                                    <span class="reward-value">{self.achievement_system.format_reward(achievement['reward'])}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No achievements available at the moment.")
            
            with tabs[1]:
                completed_achievements = []
                for achievement_id in st.session_state.user_data.get("completed_achievements", []):
                    if achievement_id in self.achievement_system.achievements:
                        completed_achievements.append(self.achievement_system.achievements[achievement_id])
                
                if completed_achievements:
                    for achievement in completed_achievements:
                        st.markdown(f"""
                            <div class="achievement-card completed {achievement['rarity'].lower()}">
                                <div class="achievement-header">
                                    <span class="achievement-icon">{achievement['icon']}</span>
                                    <h3>{achievement['name']}</h3>
                                    <span class="achievement-rarity">{achievement['rarity']}</span>
                                </div>
                                <p class="achievement-description">{achievement['description']}</p>
                                <div class="achievement-reward">
                                    <span class="reward-label">Reward:</span>
                                    <span class="reward-value">{self.achievement_system.format_reward(achievement['reward'])}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No achievements completed yet.")

        except Exception as e:
            st.error(f"Error displaying achievements: {str(e)}")

    def show_events(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Events</h1>
                    <p>Special opportunities and challenges</p>
                </div>
            """, unsafe_allow_html=True)

            # Active Events
            st.markdown("<h2>Active Events</h2>", unsafe_allow_html=True)
            if st.session_state.active_events:
                for event in st.session_state.active_events:
                    start_time = datetime.fromisoformat(event['start_time'])
                    time_left = start_time + timedelta(hours=event['duration']) - datetime.now()
                    
                    st.markdown(f"""
                        <div class="event-card {event['type']} {event['rarity'].lower()}">
                            <div class="event-header">
                                <span class="event-icon">{event['icon']}</span>
                                <h3>{event['name']}</h3>
                                <span class="event-rarity">{event['rarity']}</span>
                            </div>
                            <p class="event-description">{event['description']}</p>
                            <div class="event-timer">Time remaining: {str(time_left).split('.')[0]}</div>
                            {self.format_event_effects(event)}
                            {self.format_challenge_info(event) if event['type'] == 'challenge' else ''}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active events at the moment.")

            # Event History
            st.markdown("<h2>Event History</h2>", unsafe_allow_html=True)
            if "event_history" in st.session_state.user_data:
                for event in reversed(st.session_state.user_data["event_history"][-10:]):
                    st.markdown(f"""
                        <div class="event-history-card {event['type']} {event['rarity'].lower()}">
                            <div class="event-header">
                                <span class="event-icon">{event['icon']}</span>
                                <h3>{event['name']}</h3>
                                <span class="event-completion">{self.format_time_ago(datetime.fromisoformat(event['completed_at']))}</span>
                            </div>
                            <p class="event-description">{event['description']}</p>
                            {self.format_completion_status(event)}
                        </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error displaying events: {str(e)}")

    def show_stats(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Statistics</h1>
                    <p>Track your progress</p>
                </div>
            """, unsafe_allow_html=True)
            
            self.analytics_dashboard.display_dashboard(st.session_state.user_data)
            
        except Exception as e:
            st.error(f"Error displaying stats: {str(e)}")

    def show_settings(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Settings</h1>
                    <p>Customize your experience</p>
                </div>
            """, unsafe_allow_html=True)
            
            self.data_manager.display_settings()
            
        except Exception as e:
            st.error(f"Error displaying settings: {str(e)}")

def show_attributes(self):
    st.markdown("<h2>Attributes</h2>", unsafe_allow_html=True)
    
    # Start the grid container
    st.markdown('<div class="attribute-grid">', unsafe_allow_html=True)
    
    # Display attributes in a 2-column grid
    attributes = st.session_state.user_data["attributes"]
    for attr, value in attributes.items():
        current_rank, next_rank, progress = self.progress_tracker.calculate_rank(value)
        
        st.markdown(f"""
            <div class="attribute-card">
                <div class="attribute-header">
                    <span class="attribute-name">{attr}</span>
                    <span class="attribute-value">{value}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {progress*100}%"></div>
                </div>
                <div class="progress-details">
                    <span>Rank {current_rank} → {next_rank}</span>
                    <span>{int(progress*100)}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Close the grid container
    st.markdown('</div>', unsafe_allow_html=True)

    def format_event_effects(self, event: dict) -> str:
        if "effects" not in event:
            return ""
        
        effects_html = '<div class="event-effects">'
        for effect_type, value in event["effects"].items():
            icon = {
                "point_multiplier": "🎯",
                "attribute_boost": "⚡",
                "streak_multiplier": "🔥",
                "all_attributes_boost": "✨"
            }.get(effect_type, "📈")
            
            effects_html += f"""
                <div class="effect">
                    <span class="effect-icon">{icon}</span>
                    <span class="effect-value">{value}x</span>
                </div>
            """
        effects_html += '</div>'
        return effects_html
    def format_challenge_info(self, event: dict) -> str:
        if "challenge" not in event:
            return ""
        
        return f"""
            <div class="challenge-info">
                <h4>Challenge Requirements</h4>
                <p>{event['challenge']['description']}</p>
                {self.format_bonus_reward(event) if 'bonus_reward' in event else ''}
            </div>
        """

    def format_bonus_reward(self, event: dict) -> str:
        return f"""
            <div class="bonus-reward">
                <h4>Bonus Reward</h4>
                <p>{event['bonus_reward']['description']}</p>
            </div>
        """

    def format_completion_status(self, event: dict) -> str:
        if event["type"] != "challenge":
            return ""
        
        status = "completed" if event.get("challenge_completed") else "failed"
        icon = "✅" if status == "completed" else "❌"
        
        return f"""
            <div class="completion-status {status}">
                <span class="status-icon">{icon}</span>
                <span class="status-text">Challenge {status}</span>
            </div>
        """

    def show_templates(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Task Templates</h1>
                    <p>Create and manage task templates</p>
                </div>
            """, unsafe_allow_html=True)

            tabs = st.tabs(["Create Template", "Browse Templates"])
            
            with tabs[0]:
                self.task_template_manager.create_template_interface()
            
            with tabs[1]:
                self.task_template_manager.display_templates()

        except Exception as e:
            st.error(f"Error displaying templates: {str(e)}")

    def show_jobs(self):
        try:
            st.markdown("""
                <div class="page-header">
                    <h1>Jobs</h1>
                    <p>Career progression and opportunities</p>
                </div>
            """, unsafe_allow_html=True)

            self.job_system.display_jobs(st.session_state.user_data)

        except Exception as e:
            st.error(f"Error displaying jobs: {str(e)}")

    @staticmethod
    def format_time_ago(timestamp: datetime) -> str:
        now = datetime.now()
        delta = now - timestamp

        if delta.days > 30:
            months = delta.days // 30
            return f"{months}mo ago"
        elif delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            return "just now"

def load_css():
    """Load custom CSS file"""
    try:
        css_file = 'static/styles/main.css'
        if os.path.exists(css_file):
            with open(css_file) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        else:
            st.warning("CSS file not found. Using default styling.")
    except Exception as e:
        st.error(f"Error loading CSS: {str(e)}")

def main():
    try:
        # Page configuration
        st.set_page_config(
            page_title="ZERO2ONE - Solo Leveling System",
            page_icon="⚔️",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Load custom CSS
        load_css()

        # Initialize app
        if 'app' not in st.session_state:
            st.session_state.app = Zero2OneApp()
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Dashboard"

        # Initialize and run app
        st.session_state.app.initialize()
        st.session_state.app.run()

    except Exception as e:
        st.error("Critical error in main application:")
        st.error(str(e))
        st.error(traceback.format_exc())
        st.warning("Please try refreshing the page. If the problem persists, contact support.")

if __name__ == "__main__":
    main()