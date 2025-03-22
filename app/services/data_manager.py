#app/services/data_manager.py
import json
import os
from datetime import datetime
import streamlit as st
import shutil
from typing import Dict, Optional
import traceback

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.backup_dir = os.path.join(self.data_dir, "backups")
        self.filename = os.path.join(self.data_dir, "zero2one_data.json")
        self.max_backups = 10
        
        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

    def save_state(self):
        """Save current state with backup"""
        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"backup_{timestamp}.json")
            
            # Prepare data
            data = {
                "user_data": st.session_state.user_data,
                "tasks": st.session_state.tasks,
                "locked_attributes": st.session_state.get("locked_attributes", {}),
                "penalty_history": st.session_state.get("penalty_history", []),
                "saved_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Save main file
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Manage backup files
            self._manage_backups()
            
            return True
        except Exception as e:
            st.error(f"Error saving state: {str(e)}")
            st.error(traceback.format_exc())
            return False

    def load_state(self):
        """Load state from file with fallback to backup"""
        try:
            # Try loading main file
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    
                    # Initialize with default values if missing
                    if "user_data" not in data:
                        self.initialize_new_state()
                        return True
                    
                    # Load all data
                    st.session_state.user_data = data["user_data"]
                    st.session_state.tasks = data.get("tasks", {
                        "daily": {},
                        "weekly": {},
                        "special": {},
                        "penalty": {}
                    })
                    st.session_state.locked_attributes = data.get("locked_attributes", {})
                    st.session_state.penalty_history = data.get("penalty_history", [])
                    
                    return True
            
            # If main file fails, try latest backup
            latest_backup = self._get_latest_backup()
            if latest_backup:
                with open(latest_backup, 'r') as f:
                    data = json.load(f)
                    st.session_state.user_data = data["user_data"]
                    st.session_state.tasks = data.get("tasks", {
                        "daily": {},
                        "weekly": {},
                        "special": {},
                        "penalty": {}
                    })
                    st.session_state.locked_attributes = data.get("locked_attributes", {})
                    st.session_state.penalty_history = data.get("penalty_history", [])
                    st.warning("Main save file corrupted. Loaded from backup.")
                    return True
            
            # If no files exist, initialize new state
            self.initialize_new_state()
            return True
            
        except Exception as e:
            st.error(f"Error loading state: {str(e)}")
            st.error(traceback.format_exc())
            self.initialize_new_state()
            return False

    def initialize_new_state(self):
        """Initialize new user state"""
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
            "achievements": [],
            "completed_achievements": [],
            "job": None,
            "job_history": [],
            "active_events": [],
            "last_event_check": datetime.now().isoformat(),
            "multipliers": {
                "streak": 1.0,
                "event": 1.0,
                "job": 1.0
            }
        }

        st.session_state.tasks = {
            "daily": {},
            "weekly": {},
            "special": {},
            "penalty": {}
        }

        st.session_state.locked_attributes = {}
        st.session_state.penalty_history = []

    def _manage_backups(self):
        """Manage backup files, keeping only the most recent ones"""
        try:
            backup_files = [f for f in os.listdir(self.backup_dir) 
                          if f.startswith("backup_") and f.endswith(".json")]
            backup_files.sort(reverse=True)
            
            # Remove excess backups
            if len(backup_files) > self.max_backups:
                for old_backup in backup_files[self.max_backups:]:
                    os.remove(os.path.join(self.backup_dir, old_backup))
        except Exception as e:
            st.error(f"Error managing backups: {str(e)}")

    def _get_latest_backup(self) -> Optional[str]:
        """Get the path to the latest backup file"""
        try:
            backup_files = [f for f in os.listdir(self.backup_dir) 
                          if f.startswith("backup_") and f.endswith(".json")]
            if backup_files:
                backup_files.sort(reverse=True)
                return os.path.join(self.backup_dir, backup_files[0])
        except Exception:
            return None
        return None

    def export_data(self) -> Dict:
        """Export user data in a portable format"""
        try:
            export_data = {
                "user_data": st.session_state.user_data,
                "tasks": st.session_state.tasks,
                "locked_attributes": st.session_state.get("locked_attributes", {}),
                "penalty_history": st.session_state.get("penalty_history", []),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            return export_data
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
            return {}

    def import_data(self, data: Dict) -> bool:
        """Import user data from exported format"""
        try:
            # Validate data structure
            required_keys = ["user_data", "tasks", "exported_at", "version"]
            if not all(key in data for key in required_keys):
                st.error("Invalid data format")
                return False
            
            # Create backup before import
            self.save_state()
            
            # Update session state
            st.session_state.user_data = data["user_data"]
            st.session_state.tasks = data.get("tasks", {
                "daily": {},
                "weekly": {},
                "special": {},
                "penalty": {}
            })
            st.session_state.locked_attributes = data.get("locked_attributes", {})
            st.session_state.penalty_history = data.get("penalty_history", [])
            
            # Save imported data
            self.save_state()
            
            return True
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            return False

    def reset_progress(self) -> bool:
        """Reset all progress with confirmation"""
        try:
            # Create backup before reset
            backup_file = os.path.join(
                self.backup_dir, 
                f"pre_reset_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(backup_file, 'w') as f:
                json.dump(self.export_data(), f, indent=2)
            
            # Initialize new state
            self.initialize_new_state()
            
            # Save new state
            self.save_state()
            
            return True
        except Exception as e:
            st.error(f"Error resetting progress: {str(e)}")
            return False

    def display_settings(self):
        """Display data management settings"""
        st.markdown("<h2>Settings</h2>", unsafe_allow_html=True)
        
        # Data Management Section
        st.markdown("<h3>Data Management</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export Data
            if st.button("Export Data"):
                export_data = self.export_data()
                if export_data:
                    st.download_button(
                        "Download Progress",
                        json.dumps(export_data, indent=2),
                        "zero2one_progress.json",
                        "application/json"
                    )
        
        with col2:
            # Import Data
            uploaded_file = st.file_uploader("Import Data", type="json")
            if uploaded_file is not None:
                try:
                    import_data = json.load(uploaded_file)
                    if self.import_data(import_data):
                        st.success("Data imported successfully!")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error importing data: {str(e)}")
        
        # Backup Management
        st.markdown("<h3>Backup Management</h3>", unsafe_allow_html=True)
        
        if st.button("Create Manual Backup"):
            if self.save_state():
                st.success("Backup created successfully!")
        
        # Display existing backups
        backup_files = [f for f in os.listdir(self.backup_dir) 
                       if f.startswith("backup_") and f.endswith(".json")]
        if backup_files:
            st.markdown("<h4>Available Backups</h4>", unsafe_allow_html=True)
            for backup_file in sorted(backup_files, reverse=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(backup_file)
                with col2:
                    if st.button("Restore", key=f"restore_{backup_file}"):
                        try:
                            with open(os.path.join(self.backup_dir, backup_file), 'r') as f:
                                data = json.load(f)
                                if self.import_data(data):
                                    st.success("Backup restored successfully!")
                                    st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error restoring backup: {str(e)}")
        
        # Reset Progress
        st.markdown("<h3>Reset Progress</h3>", unsafe_allow_html=True)
        st.warning("⚠️ This action cannot be undone!")
        
        if st.button("Reset All Progress"):
            confirm = st.checkbox("I understand this will reset all progress")
            if confirm:
                if self.reset_progress():
                    st.success("Progress reset successfully!")
                    st.experimental_rerun()