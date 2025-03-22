# app/models/tasks.py
from datetime import datetime, timedelta
import random
import streamlit as st
import json
import os
import traceback
from typing import Dict, Optional

class TaskManager:
    def __init__(self):
        # Add tracking attributes to constructor
        self.task_types = {
            "daily": "🌅 Daily Tasks",
            "weekly": "📅 Weekly Tasks",
            "special": "⭐ Special Tasks"
        }
        self.severity_levels = {
            1: {"range": (1, 3), "penalty": (1, 2), "message": "Minor Setback"},
            2: {"range": (4, 7), "penalty": (3, 5), "message": "Significant Decline"},
            3: {"range": (8, float('inf')), "penalty": (6, 8), "message": "Critical Failure"}
        }
        self.load_tasks()

    def determine_severity(self, missed_days: int) -> dict:
        """Determine severity level based on missed days"""
        for level, data in self.severity_levels.items():
            if data["range"][0] <= missed_days <= data["range"][1]:
                return {
                    "level": level,
                    "penalty_range": data["penalty"],
                    "message": data["message"]
                }
        return self.severity_levels[3]  # Maximum severity for extended absence

    def load_tasks(self):
        """Load tasks from persistent storage"""
        try:
            if 'tasks' not in st.session_state:
                st.session_state.tasks = {
                    "daily": {},
                    "weekly": {},
                    "special": {}
                }
            else:
                # Ensure all task types exist
                for task_type in self.task_types.keys():
                    if task_type not in st.session_state.tasks:
                        st.session_state.tasks[task_type] = {}
            
        except Exception as e:
            st.error(f"Error loading tasks: {e}")
            st.error(traceback.format_exc())
            st.session_state.tasks = {
                "daily": {},
                "weekly": {},
                "special": {}
            }

    def update_tasks(self, user_data: Dict):
        """Update task status with progressive severity system"""
        try:
            current_time = datetime.now()
            last_active = datetime.fromisoformat(user_data.get("last_active", current_time.isoformat()))
            
            # Calculate days of inactivity
            inactive_days = (current_time.date() - last_active.date()).days
            
            if inactive_days > 0:
                # Get incomplete tasks
                incomplete_tasks = []
                for task_type, tasks in st.session_state.tasks.items():
                    incomplete_tasks.extend([
                        task for task in tasks.values()
                        if not task.get("completed", False)
                    ])
                
                if incomplete_tasks:
                    # Determine severity based on inactivity period
                    severity = self.determine_severity(inactive_days)
                    
                    # Offer makeup opportunity for first day
                    if inactive_days == 1:
                        st.warning(f"""
                        ### ⚠️ Makeup Opportunity Available
                        Complete your tasks within 12 hours to avoid penalties.
                        Tasks remaining: {len(incomplete_tasks)}
                        """)
                        
                        # Set makeup deadline
                        user_data["makeup_deadline"] = (
                            current_time + timedelta(hours=12)
                        ).isoformat()
                        
                    else:
                        # Check if makeup period has passed
                        makeup_deadline = datetime.fromisoformat(
                            user_data.get("makeup_deadline", "2000-01-01T00:00:00")
                        )
                        
                        if current_time > makeup_deadline:
                            # Apply penalties
                            penalty_points = random.randint(
                                severity["penalty_range"][0],
                                severity["penalty_range"][1]
                            )
                            
                            # Decide penalty distribution (70% single attribute, 30% all attributes)
                            if random.random() < 0.7:
                                # Single attribute penalty
                                attribute = random.choice(list(user_data["attributes"].keys()))
                                current_value = user_data["attributes"].get(attribute, 0)
                                user_data["attributes"][attribute] = max(
                                    0, current_value - penalty_points
                                )
                                
                                st.error(f"""
                                ### {severity["message"]}
                                - Inactive Days: {inactive_days}
                                - Penalty: -{penalty_points} points to {attribute}
                                - Incomplete Tasks: {len(incomplete_tasks)}
                                
                                🔥 Complete tasks within 12 hours to stop further decline!
                                """)
                            else:
                                # Distributed penalty
                                attributes = list(user_data["attributes"].keys())
                                per_attribute_penalty = penalty_points / len(attributes)
                                
                                for attr in attributes:
                                    current_value = user_data["attributes"].get(attr, 0)
                                    user_data["attributes"][attr] = max(
                                        0, current_value - per_attribute_penalty
                                    )
                                
                                st.error(f"""
                                ### {severity["message"]}
                                - Inactive Days: {inactive_days}
                                - Penalty: -{per_attribute_penalty:.1f} points to all attributes
                                - Incomplete Tasks: {len(incomplete_tasks)}
                                
                                🔥 Complete tasks within 12 hours to stop further decline!
                                """)
                
                # Reset tasks as needed
                self.reset_periodic_tasks(current_time, last_active)
            
            # Update last active timestamp
            user_data["last_active"] = current_time.isoformat()
            
            # Save state
            if 'data_manager' in st.session_state:
                st.session_state.data_manager.save_state()

        except Exception as e:
            st.error(f"Error updating tasks: {str(e)}")
            st.error(traceback.format_exc())

    def create_task_interface(self):
        """Create new task interface"""
        try:
            st.markdown("""
                <div class="section-title">
                    <h2>Create New Task</h2>
                    <p>Design your path to greatness</p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("task_creation", clear_on_submit=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    task_name = st.text_input("Task Name")
                    description = st.text_area("Description (optional)", max_chars=200)
                    
                with col2:
                    task_type = st.selectbox(
                        "Task Type",
                        options=list(self.task_types.keys()),
                        format_func=lambda x: self.task_types[x].split(' ')[1]
                    )
                    
                    attribute = st.selectbox(
                        "Attribute",
                        options=list(st.session_state.user_data["attributes"].keys())
                    )
                    
                    if task_type == "weekly":
                        frequency = st.number_input(
                            "Times per week",
                            min_value=1,
                            max_value=7,
                            value=1,
                            help="How many times per week?"
                        )
                    else:
                        frequency = 1

                if st.form_submit_button("Create Task", use_container_width=True):
                    return self.create_task(task_name, description, task_type, attribute, frequency)

        except Exception as e:
            st.error(f"Error in task creation interface: {str(e)}")
            st.error(traceback.format_exc())
            return False

    def create_task(self, task_name: str, description: str, task_type: str, 
                   attribute: str, frequency: int) -> bool:
        """Create a new task"""
        try:
            if not task_name:
                st.error("Please enter a task name")
                return False

            if self.check_duplicate_task(task_name, task_type):
                st.error("This task already exists!")
                return False

            # Ensure the task type exists
            if task_type not in st.session_state.tasks:
                st.session_state.tasks[task_type] = {}

            unique_id = f"{task_type}_{datetime.now().timestamp()}"
            points = frequency if task_type == "weekly" else 1

            task = {
                "id": unique_id,
                "name": task_name,
                "description": description,
                "type": task_type,
                "attribute": attribute,
                "points": points,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }

            st.session_state.tasks[task_type][unique_id] = task

            if 'data_manager' in st.session_state:
                st.session_state.data_manager.save_state()

            st.success("Task created successfully!")
            st.balloons()
            return True

        except Exception as e:
            st.error(f"Error creating task: {str(e)}")
            st.error(traceback.format_exc())
            return False

    def display_tasks(self):
        """Display all task categories"""
        try:
            tabs = st.tabs(list(self.task_types.values()))
            
            for i, (task_type, _) in enumerate(self.task_types.items()):
                with tabs[i]:
                    self.show_task_category(task_type)

        except Exception as e:
            st.error(f"Error displaying tasks: {str(e)}")
            st.error(traceback.format_exc())

    def show_task_category(self, category: str):
        """Display tasks for a specific category"""
        try:
            # Ensure the category exists
            if category not in st.session_state.tasks:
                st.session_state.tasks[category] = {}

            tasks = st.session_state.tasks[category]
            
            if not tasks:
                st.info(f"No {category} tasks yet. Create some tasks to begin your journey!")
                return

            # Show completion progress
            active_tasks = [task for task in tasks.values() if not task.get("completed", False)]
            completed_tasks = [task for task in tasks.values() if task.get("completed", False)]
            
            if tasks:
                progress = len(completed_tasks) / len(tasks)
                st.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {progress*100}%"></div>
                    </div>
                    <p class="progress-text">Completed: {len(completed_tasks)}/{len(tasks)}</p>
                """, unsafe_allow_html=True)

            for task in active_tasks:
                st.markdown(f"""
                    <div class="task-card">
                        <div class="task-header">
                            <h3>{task['name']}</h3>
                            <span class="task-points">+{task['points']} {task['attribute']}</span>
                        </div>
                        {f'<p class="task-description">{task["description"]}</p>' if task.get('description') else ''}
                    </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Complete", key=f"complete_{task['id']}"):
                        self.complete_task(task['id'], task, category)
                with col2:
                    if st.button("Remove", key=f"remove_{task['id']}"):
                        self.remove_task(task['id'], category)

        except Exception as e:
            st.error(f"Error showing task category: {str(e)}")
            st.error(traceback.format_exc())

    def complete_task(self, task_id: str, task: dict, task_type: str) -> bool:
        """Complete a task and award points"""
        try:
            if task_type not in st.session_state.tasks:
                return False

            stored_task = st.session_state.tasks[task_type].get(task_id)
            if not stored_task:
                return False

            if stored_task.get("completed", False):
                st.warning("Task already completed!")
                return False

            # Update task completion status
            stored_task["completed"] = True
            stored_task["completed_at"] = datetime.now().isoformat()
            
            # Get job multiplier
            job_multiplier = st.session_state.user_data.get("multipliers", {}).get("job", 1.0)
            
            # Calculate points with multiplier
            base_points = stored_task.get("points", 1)
            final_points = base_points * job_multiplier
            
            # Update attribute points
            attribute = stored_task["attribute"]
            current_value = st.session_state.user_data["attributes"].get(attribute, 0)
            st.session_state.user_data["attributes"][attribute] = current_value + final_points

            # Save state
            if 'data_manager' in st.session_state:
                st.session_state.data_manager.save_state()

            # Success message
            st.success(f"Task completed! +{final_points:.1f} {attribute} points!")
            st.balloons()
            return True

        except Exception as e:
            st.error(f"Error completing task: {str(e)}")
            st.error(traceback.format_exc())
            return False
            
       
    def remove_task(self, task_id: str, task_type: str):
        """Remove a task"""
        try:
            if task_type in st.session_state.tasks:
                del st.session_state.tasks[task_type][task_id]
                
            if 'data_manager' in st.session_state:
                st.session_state.data_manager.save_state()
                
            st.experimental_rerun()
            
        except Exception as e:
            st.error(f"Error removing task: {str(e)}")
            st.error(traceback.format_exc())

    def check_duplicate_task(self, task_name: str, task_type: str) -> bool:
        """Check for existing tasks with the same name"""
        try:
            if task_type in st.session_state.tasks:
                task_name_lower = task_name.lower()
                existing_tasks = [task["name"].lower() 
                                for task in st.session_state.tasks[task_type].values()]
                return task_name_lower in existing_tasks
            return False
        except Exception as e:
            st.error(f"Error checking for duplicate task: {str(e)}")
            st.error(traceback.format_exc())
            return False