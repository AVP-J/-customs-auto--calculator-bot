"""
State management for step-by-step interface.
"""
from enum import Enum
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UserState(Enum):
    """User states in the step-by-step interface."""
    START = "start"
    CHOOSE_VEHICLE_TYPE = "choose_vehicle_type"
    ENTER_PRICE = "enter_price"
    CHOOSE_ENGINE_TYPE = "choose_engine_type"
    CHOOSE_COUNTRY = "choose_country"
    CONFIRM_DATA = "confirm_data"
    CALCULATING = "calculating"
    SHOW_RESULT = "show_result"


class UserSession:
    """User session data."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.state = UserState.START
        self.data: Dict[str, Any] = {
            "vehicle_type": None,      # car, truck, motorcycle
            "price": None,             # in USD
            "engine_type": None,       # electric, hybrid, gasoline, diesel
            "country": None,           # china, usa, europe, japan, korea
            "currency": "USD",         # USD, CNY, EUR
            "year": None,              # vehicle year
            "calculation_result": None
        }
        self.created_at = None
        self.updated_at = None
    
    def update_state(self, new_state: UserState):
        """Update user state."""
        self.state = new_state
        logger.debug(f"User {self.user_id}: state changed to {new_state.value}")
    
    def update_data(self, key: str, value: Any):
        """Update session data."""
        self.data[key] = value
        logger.debug(f"User {self.user_id}: data[{key}] = {value}")
    
    def get_data(self, key: str) -> Any:
        """Get session data."""
        return self.data.get(key)
    
    def is_complete(self) -> bool:
        """Check if all required data is filled."""
        required_fields = ["vehicle_type", "price", "engine_type", "country"]
        return all(self.data.get(field) is not None for field in required_fields)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "user_id": self.user_id,
            "state": self.state.value,
            "data": self.data,
            "is_complete": self.is_complete()
        }


class SessionManager:
    """Manage user sessions (in-memory, will be replaced with database)."""
    
    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}
        logger.info("Session manager initialized")
    
    def get_session(self, user_id: int) -> UserSession:
        """Get or create user session."""
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(user_id)
            logger.info(f"Created new session for user {user_id}")
        return self.sessions[user_id]
    
    def update_session(self, user_id: int, **kwargs):
        """Update user session."""
        session = self.get_session(user_id)
        
        if "state" in kwargs:
            session.update_state(kwargs["state"])
        
        if "data" in kwargs:
            for key, value in kwargs["data"].items():
                session.update_data(key, value)
        
        logger.debug(f"Updated session for user {user_id}: {session.to_dict()}")
    
    def delete_session(self, user_id: int):
        """Delete user session."""
        if user_id in self.sessions:
            del self.sessions[user_id]
            logger.info(f"Deleted session for user {user_id}")
    
    def get_all_sessions(self) -> Dict[int, Dict[str, Any]]:
        """Get all sessions as dictionaries."""
        return {user_id: session.to_dict() for user_id, session in self.sessions.items()}


# Global session manager instance
session_manager = SessionManager()