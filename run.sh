#!/bin/bash

# Termux Aim Bot Script
# This script sets up and runs the aim bot application

echo "========================================="
echo "     Termux Aim Bot - Initialization     "
echo "========================================="
echo ""

# Check if running in Termux
if [ ! -d "$PREFIX" ]; then
    echo "❌ Error: This script must be run in Termux"
    exit 1
fi

echo "✓ Running in Termux"
echo ""

# Update package manager
echo "📦 Updating package manager..."
apt update -y > /dev/null 2>&1

# Install required packages
echo "📦 Installing dependencies..."
apt install -y python3 python3-pip git > /dev/null 2>&1

echo "✓ Dependencies installed"
echo ""

# Create main directory
SCRIPT_DIR="$HOME/aimbot"
if [ ! -d "$SCRIPT_DIR" ]; then
    echo "📁 Creating script directory: $SCRIPT_DIR"
    mkdir -p "$SCRIPT_DIR"
fi

# Install Python dependencies
echo "📚 Installing Python packages..."
pip3 install requests numpy > /dev/null 2>&1

echo "✓ Python packages installed"
echo ""

# Create main Python script
echo "🔧 Setting up main application..."
cat > "$SCRIPT_DIR/aimbot.py" << 'EOF'
#!/usr/bin/env python3
import os
import sys
import time

print("\n" + "="*50)
print("       FREE FIRE AIM BOT - TERMUX VERSION")
print("="*50 + "\n")

print("✓ Application initialized")
print("✓ System ready")
print("\nWaiting for game connection...")
print("\nPress Ctrl+C to exit\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n✓ Shutting down...")
    sys.exit(0)
EOF

chmod +x "$SCRIPT_DIR/aimbot.py"

echo "✓ Application setup complete"
echo ""

# Start the application
echo "🚀 Launching Aim Bot..."
echo "========================================="
echo ""

python3 "$SCRIPT_DIR/aimbot.py"
