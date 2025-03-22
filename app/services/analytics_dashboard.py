# app/services/analytics_dashboard.py

from typing import Dict, List
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd


class AnalyticsDashboard:
    def display_dashboard(self, user_data: Dict):
        st.title("Analytics Dashboard")
        
        # Overall Progress
        self.display_overall_progress(user_data)
        
        # Detailed Analysis Sections
        col1, col2 = st.columns(2)
        
        with col1:
            self.display_attribute_analysis(user_data)
            self.display_task_analysis(user_data)
        
        with col2:
            self.display_achievement_analysis(user_data)
            self.display_streak_analysis(user_data)
        
        # Activity Patterns
        st.subheader("Activity Patterns")
        self.display_activity_heatmap(user_data)

    def display_overall_progress(self, user_data: Dict):
        total_points = sum(user_data["attributes"].values())
        total_achievements = len(user_data.get("completed_achievements", []))
        current_streak = user_data.get("streak", 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Points", total_points)
        with col2:
            st.metric("Achievements", total_achievements)
        with col3:
            st.metric("Current Streak", current_streak)

    def display_attribute_analysis(self, user_data: Dict):
        st.subheader("Attribute Progress")
        
        # Create attribute progress chart
        attributes = user_data["attributes"]
        fig = go.Figure()
        
        for attr, value in attributes.items():
            fig.add_trace(go.Bar(
                name=attr,
                x=[attr],
                y=[value],
                text=[value],
                textposition='auto',
            ))
        
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def display_task_analysis(self, user_data: Dict):
        st.subheader("Task Completion")
        
        # Calculate task statistics
        total_tasks = 0
        completed_tasks = 0
        
        for task_type in ["daily", "weekly", "special"]:
            tasks = user_data["tasks"].get(task_type, {})
            total_tasks += len(tasks)
            completed_tasks += sum(1 for task in tasks.values() if task.get("completed", False))
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Display progress
        st.progress(completion_rate / 100)
        st.caption(f"Task Completion Rate: {completion_rate:.1f}%")

    def display_achievement_analysis(self, user_data: Dict):
        st.subheader("Achievement Progress")
        
        completed = user_data.get("completed_achievements", [])
        total = len(self.achievements) if hasattr(self, 'achievements') else 0
        
        if total > 0:
            completion_rate = len(completed) / total * 100
            st.progress(completion_rate / 100)
            st.caption(f"Achievement Completion: {completion_rate:.1f}%")

    def display_streak_analysis(self, user_data: Dict):
        st.subheader("Streak Analysis")
        
        current_streak = user_data.get("streak", 0)
        max_streak = user_data.get("max_streak", 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Streak", current_streak)
        with col2:
            st.metric("Best Streak", max_streak)

    def display_activity_heatmap(self, user_data: Dict):
        # Create activity heatmap
        activity_data = self.get_activity_data(user_data)
        
        fig = go.Figure(data=go.Heatmap(
            z=activity_data,
            x=[f"{i:02d}:00" for i in range(24)],
            y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title="Activity Patterns by Hour",
            height=250,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def get_activity_data(self, user_data: Dict):
        # Create 24x7 matrix for hour/day heatmap
        activity_matrix = [[0 for _ in range(24)] for _ in range(7)]
        
        # Collect activity timestamps
        timestamps = []
        
        # Task completions
        for tasks in user_data["tasks"].values():
            for task in tasks.values():
                if task.get("completed_at"):
                    timestamps.append(datetime.fromisoformat(task["completed_at"]))
        
        # Fill matrix
        for timestamp in timestamps:
            day = timestamp.weekday()
            hour = timestamp.hour
            activity_matrix[day][hour] += 1
        
        return activity_matrix