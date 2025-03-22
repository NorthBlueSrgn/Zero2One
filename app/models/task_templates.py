# app/models/task_templates.py

from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st
import json

class TaskTemplate:
    def __init__(self, name: str, task_type: str, attribute: str, points: int, 
                 description: str = "", requirements: List[str] = None, 
                 tags: List[str] = None):
        self.name = name
        self.task_type = task_type
        self.attribute = attribute
        self.points = points
        self.description = description
        self.requirements = requirements or []
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "task_type": self.task_type,
            "attribute": self.attribute,
            "points": self.points,
            "description": self.description,
            "requirements": self.requirements,
            "tags": self.tags,
            "created_at": self.created_at
        }

class TaskTemplateManager:
    def __init__(self):
        self.default_templates = {
            "workout": {
                "name": "Workout Session",
                "task_type": "daily",
                "attribute": "Physical",
                "points": 2,
                "description": "Complete a workout session",
                "requirements": ["30 minutes minimum", "Record exercises"],
                "tags": ["fitness", "health"]
            },
            "study": {
                "name": "Study Session",
                "task_type": "daily",
                "attribute": "Intelligence",
                "points": 2,
                "description": "Focused study session",
                "requirements": ["45 minutes minimum", "Take notes"],
                "tags": ["education", "focus"]
            },
            "meditation": {
                "name": "Meditation",
                "task_type": "daily",
                "attribute": "Spiritual",
                "points": 1,
                "description": "Daily meditation practice",
                "requirements": ["15 minutes minimum", "Find quiet space"],
                "tags": ["mindfulness", "peace"]
            }
        }
        self.load_templates()

    def load_templates(self):
        """Load custom templates from storage"""
        if 'custom_templates' not in st.session_state:
            st.session_state.custom_templates = {}
            # Load default templates
            for template_id, template in self.default_templates.items():
                st.session_state.custom_templates[template_id] = template

    def save_templates(self):
        """Save custom templates to storage"""
        if 'data_manager' in st.session_state:
            st.session_state.data_manager.save_state()

    def create_template_interface(self):
        """Display interface for creating custom templates"""
        st.markdown("### Create Custom Task Template")

        with st.form("template_creation", clear_on_submit=True):
            name = st.text_input("Template Name")
            task_type = st.selectbox(
                "Task Type",
                options=["daily", "weekly", "special"]
            )
            attribute = st.selectbox(
                "Primary Attribute",
                options=list(st.session_state.user_data["attributes"].keys())
            )
            points = st.number_input("Base Points", min_value=1, value=1)
            description = st.text_area("Description")

            # Dynamic requirements
            st.markdown("#### Requirements")
            num_requirements = st.number_input("Number of Requirements", min_value=0, max_value=5, value=1)
            requirements = []
            for i in range(num_requirements):
                req = st.text_input(f"Requirement {i+1}")
                if req:
                    requirements.append(req)

            # Tags
            tags_input = st.text_input("Tags (comma-separated)")
            tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

            if st.form_submit_button("Create Template"):
                if name:
                    template = TaskTemplate(
                        name=name,
                        task_type=task_type,
                        attribute=attribute,
                        points=points,
                        description=description,
                        requirements=requirements,
                        tags=tags
                    )
                    self.add_template(template)
                    st.success("Template created successfully!")
                    return True
                else:
                    st.error("Please enter a template name")
                    return False

    def display_templates(self):
        """Display available templates"""
        st.markdown("### Available Templates")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.multiselect(
                "Filter by Type",
                options=["daily", "weekly", "special"]
            )
        with col2:
            filter_attr = st.multiselect(
                "Filter by Attribute",
                options=list(st.session_state.user_data["attributes"].keys())
            )

        # Search
        search = st.text_input("Search Templates", "")

        # Display templates
        for template_id, template in st.session_state.custom_templates.items():
            if self.filter_template(template, filter_type, filter_attr, search):
                self.display_template_card(template_id, template)

    def filter_template(self, template: Dict, filter_type: List[str], 
                       filter_attr: List[str], search: str) -> bool:
        """Filter templates based on criteria"""
        if filter_type and template["task_type"] not in filter_type:
            return False
        if filter_attr and template["attribute"] not in filter_attr:
            return False
        if search:
            search_lower = search.lower()
            template_text = f"{template['name']} {template['description']} {' '.join(template['tags'])}".lower()
            if search_lower not in template_text:
                return False
        return True

    def display_template_card(self, template_id: str, template: Dict):
        """Display individual template card"""
        with st.container():
            st.markdown(f"""
                <div class="template-card">
                    <div class="template-header">
                        <h3>{template['name']}</h3>
                        <span class="template-type">{template['task_type']}</span>
                    </div>
                    <p>{template['description']}</p>
                    <div class="template-details">
                        <span>Attribute: {template['attribute']}</span>
                        <span>Points: {template['points']}</span>
                    </div>
                    <div class="template-requirements">
                        <h4>Requirements:</h4>
                        <ul>
                            {"".join([f"<li>{req}</li>" for req in template['requirements']])}
                        </ul>
                    </div>
                    <div class="template-tags">
                        {"".join([f'<span class="tag">{tag}</span>' for tag in template['tags']])}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Use Template", key=f"use_{template_id}"):
                    self.use_template(template)
            with col2:
                if st.button("Delete Template", key=f"delete_{template_id}"):
                    self.delete_template(template_id)

    def add_template(self, template: TaskTemplate):
        """Add new template to storage"""
        template_id = f"template_{datetime.now().timestamp()}"
        st.session_state.custom_templates[template_id] = template.to_dict()
        self.save_templates()

    def delete_template(self, template_id: str):
        """Delete template from storage"""
        if template_id in st.session_state.custom_templates:
            del st.session_state.custom_templates[template_id]
            self.save_templates()
            st.success("Template deleted successfully!")
            st.experimental_rerun()

    def use_template(self, template: Dict):
        """Create task from template"""
        if 'task_manager' in st.session_state:
            task_data = {
                "name": template["name"],
                "type": template["task_type"],
                "attribute": template["attribute"],
                "points": template["points"],
                "description": template["description"],
                "requirements": template["requirements"],
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            
            # Add task using task manager
            st.session_state.task_manager.add_task(task_data)
            st.success("Task created from template!")
            st.experimental_rerun()