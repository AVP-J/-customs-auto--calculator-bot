#!/usr/bin/env python3
"""
Simple script to run the Customs Calculator Bot.
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main
from src.bot.main import main

if __name__ == "__main__":
    print("🚀 Starting Customs Calculator Bot...")
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)