#app/coredatabase.py
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st

Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    attributes = Column(JSON)
    tasks = Column(JSON)
    streak = Column(Integer)
    last_active = Column(String)
    achievements = Column(JSON)
    job_history = Column(JSON)
    multipliers = Column(JSON)

class DatabaseManager:
    def __init__(self, db_path='zero2one.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_user_data(self, username, user_data):
        session = self.Session()
        try:
            user = session.query(UserModel).filter_by(username=username).first()
            if not user:
                user = UserModel(username=username)
                session.add(user)
            
            user.attributes = user_data.get('attributes', {})
            user.tasks = user_data.get('tasks', {})
            user.streak = user_data.get('streak', 0)
            user.last_active = user_data.get('last_active', '')
            user.achievements = user_data.get('achievements', [])
            user.job_history = user_data.get('job_history', [])
            user.multipliers = user_data.get('multipliers', {})
            
            session.commit()
        except Exception as e:
            session.rollback()
            st.error(f"Database save error: {e}")
        finally:
            session.close()

    def load_user_data(self, username):
        session = self.Session()
        try:
            user = session.query(UserModel).filter_by(username=username).first()
            if user:
                return {
                    'attributes': user.attributes,
                    'tasks': user.tasks,
                    'streak': user.streak,
                    'last_active': user.last_active,
                    'achievements': user.achievements,
                    'job_history': user.job_history,
                    'multipliers': user.multipliers
                }
            return None
        except Exception as e:
            st.error(f"Database load error: {e}")
            return None
        finally:
            session.close()