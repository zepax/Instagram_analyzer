#!/bin/bash

# Clean up unnecessary GUI scripts and configurations
echo "🧹 Cleaning up unnecessary browser scripts..."

# Remove old GUI-related files
echo "📁 Removing old GUI scripts..."
rm -f .devcontainer/start-gui.sh 2>/dev/null && echo "  ✅ Removed start-gui.sh" || echo "  ⚠️  start-gui.sh not found"
rm -f .devcontainer/view-analysis.sh 2>/dev/null && echo "  ✅ Removed view-analysis.sh" || echo "  ⚠️  view-analysis.sh not found"
rm -f .devcontainer/install-novnc.sh 2>/dev/null && echo "  ✅ Removed install-novnc.sh" || echo "  ⚠️  install-novnc.sh not found"
rm -f .devcontainer/demo.sh 2>/dev/null && echo "  ✅ Removed demo.sh" || echo "  ⚠️  demo.sh not found"

# Clean up bashrc if it contains old GUI functions
echo "🔧 Cleaning up bashrc..."
if grep -q "Instagram Analyzer GUI Functions" ~/.bashrc 2>/dev/null; then
    # Create a backup
    cp ~/.bashrc ~/.bashrc.backup

    # Remove the old GUI section
    sed -i '/# Instagram Analyzer GUI Functions/,/^fi$/d' ~/.bashrc
    echo "  ✅ Removed old GUI functions from bashrc"
else
    echo "  ✅ No old GUI functions found in bashrc"
fi

# Update devcontainer.json to remove unnecessary ports
echo "🔧 Updating devcontainer.json..."
if grep -q "5900\|6080" .devcontainer/devcontainer.json; then
    # Remove VNC ports since we're using VS Code extensions now
    sed -i '/5900,/d' .devcontainer/devcontainer.json
    sed -i '/6080/d' .devcontainer/devcontainer.json
    sed -i '/"5900":/,+4d' .devcontainer/devcontainer.json
    sed -i '/"6080":/,+4d' .devcontainer/devcontainer.json
    echo "  ✅ Removed VNC ports from devcontainer.json"
else
    echo "  ✅ No VNC ports found in devcontainer.json"
fi

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "🌐 Current HTML viewing setup:"
echo "  • VS Code Extensions: Microsoft Edge Tools + Live Server"
echo "  • Script: .devcontainer/view-html.sh"
echo "  • Setup: .devcontainer/setup-vscode-html.sh"
echo ""
echo "💡 To view HTML files:"
echo "  1. Right-click HTML file in VS Code Explorer"
echo "  2. Select 'Open with Live Server'"
echo "  3. View at http://localhost:5500"
echo ""
