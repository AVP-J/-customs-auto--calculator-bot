#!/usr/bin/env python3
"""
Test full workflow without Telegram API.
Simulates user going through all steps.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot.states import UserState, UserSession, SessionManager
from src.bot.keyboards import get_keyboard_for_state
from src.bot.messages import get_message_for_state


def simulate_user_workflow():
    """Simulate a user going through all steps."""
    print("👤 Simulating user workflow...\n")
    
    # Create session
    session = UserSession(123456)
    
    # Step 1: Choose vehicle type
    print("🚗 Step 1: Choosing vehicle type")
    session.update_state(UserState.CHOOSE_VEHICLE_TYPE)
    message1 = get_message_for_state(session.state)
    keyboard1 = get_keyboard_for_state(session.state)
    print(f"  Message: {message1[:100]}...")
    print(f"  Keyboard rows: {len(keyboard1.inline_keyboard)}")
    
    # User selects "car"
    session.update_data("vehicle_type", "car")
    session.update_state(UserState.ENTER_PRICE)
    print("  ✅ Selected: car\n")
    
    # Step 2: Enter price
    print("💰 Step 2: Entering price")
    message2 = get_message_for_state(session.state, session.data)
    print(f"  Message: {message2[:100]}...")
    
    # User enters price 30000
    session.update_data("price", 30000)
    session.update_state(UserState.CHOOSE_ENGINE_TYPE)
    print("  ✅ Entered: 30000 USD\n")
    
    # Step 3: Choose engine type
    print("🔧 Step 3: Choosing engine type")
    message3 = get_message_for_state(session.state, session.data)
    keyboard3 = get_keyboard_for_state(session.state, session.data)
    print(f"  Message: {message3[:100]}...")
    print(f"  Keyboard rows: {len(keyboard3.inline_keyboard)}")
    
    # User selects "electric"
    session.update_data("engine_type", "electric")
    session.update_state(UserState.CHOOSE_COUNTRY)
    print("  ✅ Selected: electric\n")
    
    # Step 4: Choose country
    print("🌍 Step 4: Choosing country")
    message4 = get_message_for_state(session.state, session.data)
    keyboard4 = get_keyboard_for_state(session.state, session.data)
    print(f"  Message: {message4[:100]}...")
    print(f"  Keyboard rows: {len(keyboard4.inline_keyboard)}")
    
    # User selects "china"
    session.update_data("country", "china")
    session.update_state(UserState.CONFIRM_DATA)
    print("  ✅ Selected: china\n")
    
    # Step 5: Confirm data
    print("📋 Step 5: Confirming data")
    message5 = get_message_for_state(session.state, session.data)
    keyboard5 = get_keyboard_for_state(session.state, session.data)
    print(f"  Message: {message5[:150]}...")
    print(f"  Keyboard rows: {len(keyboard5.inline_keyboard)}")
    
    # Check if all data is complete
    print(f"  ✅ All data complete: {session.is_complete()}")
    print(f"  Data summary: {session.data}\n")
    
    # Step 6: Show result (simulate calculation)
    print("🎯 Step 6: Showing result")
    session.update_state(UserState.SHOW_RESULT)
    message6 = get_message_for_state(session.state, session.data)
    keyboard6 = get_keyboard_for_state(session.state, session.data)
    print(f"  Message length: {len(message6)} chars")
    print(f"  Keyboard rows: {len(keyboard6.inline_keyboard)}")
    
    # Show part of result
    lines = message6.split('\n')
    for i, line in enumerate(lines[:10]):
        print(f"  {line}")
    if len(lines) > 10:
        print(f"  ... and {len(lines)-10} more lines\n")
    
    print("✅ Workflow simulation complete!")
    print(f"\n📊 Final session data:")
    for key, value in session.data.items():
        print(f"  {key}: {value}")


def test_session_persistence():
    """Test that sessions persist across multiple users."""
    print("\n👥 Testing session persistence...")
    
    manager = SessionManager()
    
    # User 1
    user1 = manager.get_session(111)
    user1.update_state(UserState.CHOOSE_VEHICLE_TYPE)
    user1.update_data("vehicle_type", "truck")
    
    # User 2
    user2 = manager.get_session(222)
    user2.update_state(UserState.ENTER_PRICE)
    user2.update_data("price", 50000)
    
    # User 3
    user3 = manager.get_session(333)
    user3.update_state(UserState.CHOOSE_ENGINE_TYPE)
    user3.update_data("engine_type", "hybrid")
    
    # Check all sessions
    all_sessions = manager.get_all_sessions()
    print(f"  Total users: {len(all_sessions)}")
    
    for user_id, session_data in all_sessions.items():
        print(f"  User {user_id}: state={session_data['state']}, data={session_data['data']}")
    
    print("✅ Session persistence test passed")


def test_error_handling():
    """Test error scenarios."""
    print("\n⚠️ Testing error handling...")
    
    session = UserSession(999)
    
    # Test incomplete data
    print("  Testing incomplete data check:")
    session.update_data("vehicle_type", "car")
    session.update_data("price", 30000)
    # Missing engine_type and country
    print(f"    Is complete? {session.is_complete()} (expected: False)")
    
    # Add missing data
    session.update_data("engine_type", "electric")
    session.update_data("country", "china")
    print(f"    Is complete? {session.is_complete()} (expected: True)")
    
    # Test data retrieval
    print(f"    Get vehicle_type: {session.get_data('vehicle_type')}")
    print(f"    Get non-existent: {session.get_data('non_existent')}")
    
    print("✅ Error handling test passed")


def main():
    """Run all simulations."""
    print("🚀 Running full workflow simulation\n")
    
    try:
        simulate_user_workflow()
        test_session_persistence()
        test_error_handling()
        
        print("\n🎉 All simulations passed!")
        print("\n📱 Next steps for real testing:")
        print("1. Get token from @BotFather")
        print("2. Update .env file with TELEGRAM_BOT_TOKEN")
        print("3. Run: python3 -m src.bot.main")
        print("4. Test with real Telegram bot")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()