#app/services/progress_tracker.py
from typing import Dict, List, Tuple
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import pandas as pd

class ProgressTracker:
    def __init__(self):
        self.stat_categories = {
            "Tasks": self.get_task_stats,
            "Attributes": self.get_attribute_stats,
            "Achievements": self.get_achievement_stats,
            "Career": self.get_career_stats,
            "Penalties": self.get_penalty_stats
        }
        
        self.rank_thresholds = {
            "E": 0,
            "D": 85,
            "C": 170,
            "B": 255,
            "A": 340,
            "S": 425,
            "SS": 510,
            "SSS": 595
        }

    def calculate_rank(self, value: int) -> Tuple[str, str, float]:
        """Calculate current rank, next rank, and progress percentage"""
        current_rank = "E"
        next_rank = "D"
        progress = 0.0
        
        # Find current and next rank
        ranks = list(self.rank_thresholds.items())
        for i, (rank, threshold) in enumerate(ranks):
            if value >= threshold:
                current_rank = rank
                next_rank = ranks[i + 1][0] if i < len(ranks) - 1 else rank
        
        # Calculate progress percentage
        if current_rank != "SSS":
            current_threshold = self.rank_thresholds[current_rank]
            next_threshold = self.rank_thresholds[next_rank]
            progress = (value - current_threshold) / (next_threshold - current_threshold)
            progress = max(0.0, min(1.0, progress))  # Clamp between 0 and 1
        else:
            progress = 1.0
        
        return current_rank, next_rank, progress

    def create_radar_chart(self, attributes: dict) -> go.Figure:
        """Create radar chart based on attribute ranks"""
        values = []
        ranks = []
        for attr_value in attributes.values():
            rank, _, _ = self.calculate_rank(attr_value)
            rank_values = {
                "E": 1, "D": 2, "C": 3, "B": 4,
                "A": 5, "S": 6, "SS": 7, "SSS": 8
            }
            values.append(rank_values.get(rank, 0))
            ranks.append(rank)

        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=list(attributes.keys()),
            fill='toself',
            line_color='rgba(139, 92, 246, 1)',
            fillcolor='rgba(139, 92, 246, 0.3)',
            hovertemplate="<b>%{theta}</b><br>" +
                         "Rank: %{customdata}<br>" +
                         "Points: %{text}<extra></extra>",
            customdata=ranks,
            text=[str(attributes[attr]) for attr in attributes.keys()]
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 8],
                    ticktext=["", "E", "D", "C", "B", "A", "S", "SS", "SSS"],
                    tickvals=[0, 1, 2, 3, 4, 5, 6, 7, 8]
                )
            ),
            showlegend=False,
            title="Attribute Ranks",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        return fig

    def get_task_stats(self, user_data: Dict) -> Dict:
        """Get detailed task completion statistics"""
        stats = {
            "total": 0,
            "completed": 0,
            "daily_completed": 0,
            "weekly_completed": 0,
            "streak": user_data.get("streak", 0)
        }
        
        for task_type, tasks in user_data["tasks"].items():
            for task in tasks.values():
                stats["total"] += 1
                if task.get("completed"):
                    stats["completed"] += 1
                    if task_type == "daily":
                        stats["daily_completed"] += 1
                    elif task_type == "weekly":
                        stats["weekly_completed"] += 1
        
        stats["completion_rate"] = (stats["completed"] / stats["total"]) if stats["total"] > 0 else 0
        return stats

    def get_attribute_stats(self, user_data: Dict) -> Dict:
        """Get detailed attribute statistics"""
        attributes = user_data["attributes"]
        highest_attr = max(attributes.items(), key=lambda x: x[1])
        
        return {
            "highest_attribute": highest_attr[0],
            "highest_value": highest_attr[1],
            "total_points": sum(attributes.values()),
            "average_points": sum(attributes.values()) / len(attributes),
            "ranks": {attr: self.calculate_rank(val)[0] 
                     for attr, val in attributes.items()}
        }

    def get_achievement_stats(self, user_data: Dict) -> Dict:
        """Get detailed achievement statistics"""
        completed = user_data.get("completed_achievements", [])
        return {
            "total_completed": len(completed),
            "recent_achievements": completed[-3:] if completed else [],
            "completion_rate": len(completed) / len(self.achievements) 
                             if hasattr(self, 'achievements') else 0
        }

    def get_career_stats(self, user_data: Dict) -> Dict:
        """Get detailed career progression statistics"""
        job_history = user_data.get("job_history", [])
        current_job = user_data.get("current_job")
        
        return {
            "current_job": current_job,
            "jobs_held": len(job_history),
            "job_history": job_history,
            "average_job_duration": self.calculate_average_job_duration(job_history)
        }

    def get_penalty_stats(self, user_data: Dict) -> Dict:
        """Get penalty-related statistics"""
        penalty_history = user_data.get("penalty_history", [])
        
        total_penalties = len(penalty_history)
        if total_penalties == 0:
            return {
                "total_penalties": 0,
                "average_level": 0,
                "completion_rate": 0,
                "current_streak": "No penalties"
            }

        completed_penalties = sum(1 for p in penalty_history if p.get("completed", False))
        current_streak = 0
        for penalty in reversed(penalty_history):
            if penalty.get("completed", False):
                current_streak += 1
            else:
                break

        return {
            "total_penalties": total_penalties,
            "average_level": sum(p["level"] for p in penalty_history) / total_penalties,
            "completion_rate": (completed_penalties / total_penalties) * 100,
            "current_streak": f"{current_streak} completed"
        }

def display_stats_page(self, user_data: Dict):
    """Display comprehensive statistics page"""
    # Main container with dark theme
    st.markdown("""
        <div class="stats-container">
            <div class="stats-header">
                <h1>Progress Analytics</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Create two columns for main stats
    col1, col2 = st.columns([2, 1])

    with col1:
        # Radar Chart (Enhanced)
        fig = self.create_enhanced_radar_chart(user_data["attributes"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Overall Progress Summary
        st.markdown("### Overall Progress")
        total_points = sum(user_data["attributes"].values())
        avg_rank, next_rank, progress = self.calculate_rank(total_points // len(user_data["attributes"]))
        
        # Progress Metrics
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Average Rank", avg_rank)
            st.metric("Total Points", total_points)
        with metrics_col2:
            st.metric("Next Rank", next_rank)
            st.metric("Progress", f"{progress*100:.1f}%")

    # Detailed Stats Section
    st.markdown("---")
    st.markdown("### Detailed Statistics")

    # Create three columns for detailed stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Attribute Rankings")
        for attr, value in user_data["attributes"].items():
            rank, next_rank, prog = self.calculate_rank(value)
            st.markdown(f"""
                <div class="rank-card">
                    <div class="rank-header">
                        <span class="attr-name">{attr}</span>
                        <span class="rank-badge rank-{rank.lower()}">{rank}</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {prog*100}%"></div>
                    </div>
                    <div class="rank-details">
                        <span>{value} pts</span>
                        <span>{int(prog*100)}% to {next_rank}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Task Completion")
        task_stats = self.get_task_stats(user_data)
        
        # Task completion chart
        task_fig = go.Figure()
        task_fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=task_stats["completion_rate"] * 100,
            title={'text': "Completion Rate"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "rgba(139, 92, 246, 0.8)"},
                   'threshold': {
                       'line': {'color': "white", 'width': 2},
                       'thickness': 0.75,
                       'value': 80}}))
        task_fig.update_layout(height=250)
        st.plotly_chart(task_fig, use_container_width=True)

        # Task breakdown
        st.markdown(f"""
            <div class="task-stats">
                <div class="stat-item">
                    <span>Daily Tasks</span>
                    <span>{task_stats['daily_completed']}</span>
                </div>
                <div class="stat-item">
                    <span>Weekly Tasks</span>
                    <span>{task_stats['weekly_completed']}</span>
                </div>
                <div class="stat-item">
                    <span>Current Streak</span>
                    <span>{task_stats['streak']} days</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("#### Achievement Progress")
        achievement_stats = self.get_achievement_stats(user_data)
        
        # Achievement progress chart
        achievement_fig = go.Figure()
        achievement_fig.add_trace(go.Indicator(
            mode="number+delta",
            value=achievement_stats["total_completed"],
            delta={'reference': 0, 'relative': True},
            title={'text': "Achievements Unlocked"}))
        achievement_fig.update_layout(height=250)
        st.plotly_chart(achievement_fig, use_container_width=True)

        # Recent achievements
        st.markdown("##### Recent Achievements")
        for achievement in achievement_stats["recent_achievements"][-3:]:
            st.markdown(f"""
                <div class="achievement-item">
                    <span class="achievement-icon">🏆</span>
                    <span>{achievement}</span>
                </div>
            """, unsafe_allow_html=True)

    # Timeline Section
    st.markdown("---")
    st.markdown("### Progress Timeline")
    timeline_fig = self.create_progress_timeline(user_data)
    st.plotly_chart(timeline_fig, use_container_width=True)

def create_enhanced_radar_chart(self, attributes: dict) -> go.Figure:
    """Create an enhanced radar chart with better visuals"""
    values = []
    ranks = []
    for attr_value in attributes.values():
        rank, _, _ = self.calculate_rank(attr_value)
        rank_values = {
            "E": 1, "D": 2, "C": 3, "B": 4,
            "A": 5, "S": 6, "SS": 7, "SSS": 8
        }
        values.append(rank_values.get(rank, 0))
        ranks.append(rank)

    # Add first value again to close the shape
    values.append(values[0])
    ranks.append(ranks[0])
    attributes_list = list(attributes.keys())
    attributes_list.append(attributes_list[0])

    fig = go.Figure()

    # Add main attribute plot
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=attributes_list,
        fill='toself',
        line=dict(color='rgba(139, 92, 246, 1)', width=2),
        fillcolor='rgba(139, 92, 246, 0.3)',
        name='Current Ranks'
    ))

    # Add rank circles
    for rank_value in range(1, 9):
        fig.add_trace(go.Scatterpolar(
            r=[rank_value] * (len(attributes) + 1),
            theta=attributes_list,
            mode='lines',
            line=dict(color='rgba(255, 255, 255, 0.1)', width=1),
            showlegend=False
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 8],
                ticktext=["", "E", "D", "C", "B", "A", "S", "SS", "SSS"],
                tickvals=[0, 1, 2, 3, 4, 5, 6, 7, 8],
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)'
            ),
            bgcolor='rgba(0, 0, 0, 0)'
        ),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=10, b=10),
        showlegend=False
    )

    return fig    

    def display_stat_card(self, title: str, stats: Dict):
        """Display a statistics card with formatted content"""
        st.markdown(f"""
            <div class="stat-card">
                <h3>{title}</h3>
                <div class="stat-content">
                    {self.format_stats(stats)}
                </div>
            </div>
        """, unsafe_allow_html=True)

    def display_attribute_breakdown(self, user_data: Dict):
        """Display detailed attribute analysis"""
        st.markdown("<h3>Attribute Breakdown</h3>", unsafe_allow_html=True)
        
        for attr, value in user_data["attributes"].items():
            current_rank, next_rank, progress = self.calculate_rank(value)
            
            st.markdown(f"""
                <div class="attribute-breakdown">
                    <div class="attribute-header">
                        <span class="attribute-name">{attr}</span>
                        <span class="attribute-rank">Rank {current_rank}</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: {progress * 100}%"></div>
                    </div>
                    <div class="attribute-details">
                        <span>{value} points</span>
                        <span>{int(progress * 100)}% to {next_rank}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def display_achievement_breakdown(self, user_data: Dict):
        """Display detailed achievement analysis"""
        st.markdown("<h3>Achievement Progress</h3>", unsafe_allow_html=True)
        
        completed = set(user_data.get("completed_achievements", []))
        total = len(self.achievements) if hasattr(self, 'achievements') else 0
        
        if total > 0:
            completion_rate = len(completed) / total * 100
            st.progress(completion_rate / 100)
            st.markdown(f"Completed: {len(completed)}/{total} ({completion_rate:.1f}%)")

    @staticmethod
    def calculate_average_job_duration(job_history: List[Dict]) -> float:
        """Calculate average duration of jobs held"""
        if not job_history:
            return 0
            
        durations = []
        for i, job in enumerate(job_history):
            start = datetime.fromisoformat(job["accepted_at"])
            end = (datetime.fromisoformat(job_history[i+1]["accepted_at"]) 
                   if i < len(job_history) - 1 else datetime.now())
            duration = (end - start).days
            durations.append(duration)
            
        return sum(durations) / len(durations)

    @staticmethod
    def format_stats(stats: Dict) -> str:
        """Format statistics for display"""
        formatted = []
        for key, value in stats.items():
            if isinstance(value, float):
                formatted.append(f"<div class='stat-item'>"
                              f"<span class='stat-label'>{key.replace('_', ' ').title()}</span>"
                              f"<span class='stat-value'>{value:.2f}</span></div>")
            elif isinstance(value, (list, dict)):
                continue  # Skip complex values
            else:
                formatted.append(f"<div class='stat-item'>"
                              f"<span class='stat-label'>{key.replace('_', ' ').title()}</span>"
                              f"<span class='stat-value'>{value}</span></div>")
        return "".join(formatted)