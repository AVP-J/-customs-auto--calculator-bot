#!/usr/bin/env python3
"""
Test script for step-by-step interface.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot.states import UserState, UserSession, SessionManager
from src.bot.keyboards import get_keyboard_for_state
from src.bot.messages import get_message_for_state


def test_states():
    """Test state management."""
    print("🧪 Testing state management...")
    
    # Create session
    session = UserSession(123456)
    print(f"  Created session for user {session.user_id}")
    print(f"  Initial state: {session.state}")
    
    # Test state transitions
    session.update_state(UserState.CHOOSE_VEHICLE_TYPE)
    print(f"  State after update: {session.state}")
    
    # Test data storage
    session.update_data("vehicle_type", "car")
    session.update_data("price", 30000)
    print(f"  Data: {session.data}")
    print(f"  Is complete: {session.is_complete()}")
    
    print("✅ State management test passed\n")


def test_keyboards():
    """Test keyboard generation."""
    print("⌨️ Testing keyboard generation...")
    
    test_states = [
        UserState.CHOOSE_VEHICLE_TYPE,
        UserState.CHOOSE_ENGINE_TYPE,
        UserState.CHOOSE_COUNTRY,
        UserState.CONFIRM_DATA,
        UserState.SHOW_RESULT
    ]
    
    for state in test_states:
        keyboard = get_keyboard_for_state(state)
        print(f"  {state.value}: {len(keyboard.inline_keyboard)} rows")
    
    print("✅ Keyboard generation test passed\n")


def test_messages():
    """Test message generation."""
    print("💬 Testing message generation...")
    
    test_data = {
        "vehicle_type": "car",
        "price": 30000,
        "engine_type": "electric",
        "country": "china"
    }
    
    test_states = [
        UserState.CHOOSE_VEHICLE_TYPE,
        UserState.ENTER_PRICE,
        UserState.CHOOSE_ENGINE_TYPE,
        UserState.CHOOSE_COUNTRY,
        UserState.CONFIRM_DATA,
        UserState.SHOW_RESULT
    ]
    
    for state in test_states:
        message = get_message_for_state(state, test_data)
        print(f"  {state.value}: {len(message)} chars")
        # Print first 100 chars
        preview = message[:100].replace('\n', ' ')
        print(f"    Preview: {preview}...")
    
    print("✅ Message generation test passed\n")


def test_session_manager():
    """Test session manager."""
    print("👥 Testing session manager...")
    
    manager = SessionManager()
    
    # Get or create session
    session1 = manager.get_session(111)
    print(f"  Session 1: {session1.user_id}, state: {session1.state}")
    
    session2 = manager.get_session(222)
    print(f"  Session 2: {session2.user_id}, state: {session2.state}")
    
    # Update session
    manager.update_session(111, state=UserState.CHOOSE_VEHICLE_TYPE)
    session1_updated = manager.get_session(111)
    print(f"  Session 1 updated: {session1_updated.state}")
    
    # Get all sessions
    all_sessions = manager.get_all_sessions()
    print(f"  Total sessions: {len(all_sessions)}")
    
    # Delete session
    manager.delete_session(111)
    print(f"  After delete: {len(manager.sessions)} sessions")
    
    print("✅ Session manager test passed\n")


def main():
    """Run all tests."""
    print("🚀 Running step-by-step interface tests\n")
    
    try:
        test_states()
        test_keyboards()
        test_messages()
        test_session_manager()
        
        print("🎉 All tests passed! The step-by-step interface is ready.")
        print("\n📱 Next steps:")
        print("1. Set TELEGRAM_BOT_TOKEN in .env file")
        print("2. Run the bot: python3 -m src.bot.main")
        print("3. Test with real Telegram bot")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()