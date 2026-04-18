#!/bin/bash
# Management script for Customs Calculator Bot

PROJECT_DIR="/Users/jarvis/.openclaw/workspacesk-proj-d_KYutoeMeow7LUKRKp-D12q_KmmviQ8zyilVKY-wJIsP62VfJpZtx8nmnNZd8ezeGDPXP2Yo5T3BlbkFJXw0rL0LknE0zFpOslS5kdCHg5xhDNz98vp6cnSCXuWN4lhRtSySJctzElD7OpyBAsBuQII4fkA/customs_calculator_project"
SERVICE_FILE="$PROJECT_DIR/deployment/customs-bot.service"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.jarvis.customsbot.plist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[*]${NC} $1"
}

case "$1" in
    install)
        print_status "Installing Customs Calculator Bot service..."
        
        # Create logs directory
        mkdir -p "$PROJECT_DIR/logs"
        
        # Create LaunchAgent plist file
        cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jarvis.customsbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/venv/bin/python</string>
        <string>$PROJECT_DIR/start_bot_simple.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/bot.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/bot-error.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>RestartInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF
        
        # Load the service
        launchctl load "$PLIST_FILE"
        
        # Start the service
        launchctl start com.jarvis.customsbot
        
        print_status "Service installed and started!"
        print_status "Logs: $PROJECT_DIR/logs/"
        print_status "Check status: $0 status"
        ;;
    
    start)
        print_status "Starting Customs Calculator Bot..."
        launchctl start com.jarvis.customsbot
        sleep 2
        $0 status
        ;;
    
    stop)
        print_status "Stopping Customs Calculator Bot..."
        launchctl stop com.jarvis.customsbot
        sleep 2
        $0 status
        ;;
    
    restart)
        print_status "Restarting Customs Calculator Bot..."
        launchctl stop com.jarvis.customsbot
        sleep 2
        launchctl start com.jarvis.customsbot
        sleep 2
        $0 status
        ;;
    
    status)
        print_status "Checking Customs Calculator Bot status..."
        
        # Check if service is loaded
        if launchctl list | grep -q "com.jarvis.customsbot"; then
            print_status "Service is loaded"
        else
            print_error "Service is not loaded"
        fi
        
        # Check if service is running
        SERVICE_STATUS=$(launchctl list com.jarvis.customsbot 2>/dev/null | grep -E "^\"PID\"")
        if [ -n "$SERVICE_STATUS" ]; then
            print_status "Service is running"
        else
            print_error "Service is not running"
        fi
        
        # Check logs
        if [ -f "$PROJECT_DIR/logs/bot.log" ]; then
            LOG_SIZE=$(stat -f%z "$PROJECT_DIR/logs/bot.log" 2>/dev/null || echo "0")
            if [ "$LOG_SIZE" -gt 0 ]; then
                print_status "Log file exists ($LOG_SIZE bytes)"
                echo "=== Last 5 lines of bot.log ==="
                tail -5 "$PROJECT_DIR/logs/bot.log"
                echo "==============================="
            else
                print_warning "Log file exists but is empty"
            fi
        else
            print_warning "Log file not found"
        fi
        
        # Check bot API
        BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN "$PROJECT_DIR/.env" | cut -d= -f2)
        if curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe" | grep -q '"ok":true'; then
            print_status "Bot is accessible via Telegram API"
        else
            print_error "Bot is not accessible via Telegram API"
        fi
        ;;
    
    logs)
        print_status "Showing bot logs..."
        if [ -f "$PROJECT_DIR/logs/bot.log" ]; then
            tail -50 "$PROJECT_DIR/logs/bot.log"
        else
            print_error "Log file not found: $PROJECT_DIR/logs/bot.log"
        fi
        ;;
    
    uninstall)
        print_status "Uninstalling Customs Calculator Bot service..."
        
        # Stop service
        launchctl stop com.jarvis.customsbot 2>/dev/null
        
        # Unload service
        launchctl unload "$PLIST_FILE" 2>/dev/null
        
        # Remove plist file
        rm -f "$PLIST_FILE"
        
        print_status "Service uninstalled!"
        ;;
    
    *)
        echo "Usage: $0 {install|start|stop|restart|status|logs|uninstall}"
        echo ""
        echo "Commands:"
        echo "  install   - Install and start the bot as a service"
        echo "  start     - Start the bot service"
        echo "  stop      - Stop the bot service"
        echo "  restart   - Restart the bot service"
        echo "  status    - Check bot status and logs"
        echo "  logs      - Show bot logs"
        echo "  uninstall - Remove the bot service"
        exit 1
        ;;
esac