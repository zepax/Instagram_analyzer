#!/bin/bash

# Instagram Analyzer HTML Viewer for VS Code
# Uses VS Code extensions to view HTML reports directly in the editor

# Default directories to search for analysis files
ANALYSIS_DIRS=(
    "output"
    "final_analysis"
    "debug_analysis"
    "debug_analysis2"
    "debug_analysis3"
    "debug_analysis4"
    "debug_analysis5"
    "debug_analysis6"
    "debug_analysis7"
    "debug_analysis9"
    "debug_analysis10"
    "mi_analisis_personalizado"
    "test_output"
)

# Function to find analysis files
find_analysis_files() {
    echo "🔍 Searching for Instagram analysis files..."
    local found_files=()

    for dir in "${ANALYSIS_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            local html_file="$dir/instagram_analysis.html"
            if [ -f "$html_file" ]; then
                found_files+=("$html_file")
                echo "  ✅ Found: $html_file"
            fi
        fi
    done

    # Also search for any HTML files in current directory
    local other_html=($(find . -maxdepth 2 -name "*.html" -not -path "./.git/*" -not -path "./htmlcov/*" 2>/dev/null))
    for file in "${other_html[@]}"; do
        if [[ ! " ${found_files[@]} " =~ " ${file} " ]]; then
            found_files+=("$file")
            echo "  📄 Found: $file"
        fi
    done

    if [ ${#found_files[@]} -eq 0 ]; then
        echo "  ❌ No HTML analysis files found"
        echo ""
        echo "💡 To generate an analysis:"
        echo "  poetry run python examples/analisis_personalizado.py"
        echo ""
        return 1
    fi

    echo ""
    echo "📁 Found ${#found_files[@]} HTML file(s)"

    # Return the files array
    printf '%s\n' "${found_files[@]}"
}

# Function to display file selection menu
select_file() {
    local files=("$@")

    if [ ${#files[@]} -eq 1 ]; then
        echo "📂 Opening: ${files[0]}"
        echo "${files[0]}"
        return 0
    fi

    echo "📋 Multiple files found. Please select one:"
    echo ""

    for i in "${!files[@]}"; do
        local file="${files[$i]}"
        local size=""
        if [ -f "$file" ]; then
            size=$(du -h "$file" 2>/dev/null | cut -f1)
            size=" (${size})"
        fi
        echo "  $((i+1))) $file$size"
    done
    echo ""

    while true; do
        read -p "Enter selection (1-${#files[@]}): " selection

        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le ${#files[@]} ]; then
            local selected_file="${files[$((selection-1))]}"
            echo "📂 Selected: $selected_file"
            echo "$selected_file"
            return 0
        else
            echo "❌ Invalid selection. Please enter a number between 1 and ${#files[@]}"
        fi
    done
}

# Function to get file info
get_file_info() {
    local file="$1"
    if [ -f "$file" ]; then
        local size=$(du -h "$file" 2>/dev/null | cut -f1)
        local modified=$(stat -c %y "$file" 2>/dev/null | cut -d. -f1)
        echo "📊 File info: $size, modified $modified"
    fi
}

# Function to open file with VS Code Edge extension
open_with_edge() {
    local file="$1"
    local absolute_path=$(realpath "$file")

    echo "🌐 Opening HTML file with VS Code..."
    echo "📁 File: $absolute_path"

    # Method 1: Open with Live Server (recommended for interactive content)
    echo ""
    echo "🚀 Method 1: Live Server (Recommended)"
    echo "  1. Right-click on '$file' in VS Code Explorer"
    echo "  2. Select 'Open with Live Server'"
    echo "  3. The file will open in VS Code's integrated browser"

    # Method 2: Open with Edge DevTools extension
    echo ""
    echo "🔧 Method 2: Edge DevTools"
    echo "  1. Open the file in VS Code: '$file'"
    echo "  2. Press Ctrl+Shift+P (or Cmd+Shift+P on Mac)"
    echo "  3. Type 'Microsoft Edge Tools: Open Source in Microsoft Edge'"
    echo "  4. The file will open in Edge DevTools panel"

    # Method 3: Preview in VS Code
    echo ""
    echo "👁️  Method 3: VS Code Preview"
    echo "  1. Open '$file' in VS Code"
    echo "  2. Press Ctrl+Shift+V (or Cmd+Shift+V on Mac)"
    echo "  3. The file will preview in VS Code's HTML preview"

    # Open the file in VS Code editor
    if command -v code &> /dev/null; then
        echo ""
        echo "📝 Opening file in VS Code editor..."
        code "$absolute_path"
    else
        echo ""
        echo "💡 The file is ready to be opened in VS Code manually"
    fi
}

# Function to create VS Code tasks for HTML viewing
create_vscode_tasks() {
    echo "⚙️  Creating VS Code tasks for HTML viewing..."

    local tasks_dir=".vscode"
    local tasks_file="$tasks_dir/tasks.json"

    # Create .vscode directory if it doesn't exist
    mkdir -p "$tasks_dir"

    # Check if tasks.json exists
    if [ -f "$tasks_file" ]; then
        echo "  ✅ VS Code tasks.json already exists"
        echo "  💡 You can manually add HTML viewing tasks if needed"
        return 0
    fi

    # Create tasks.json with HTML viewing tasks
    cat > "$tasks_file" << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Open HTML with Live Server",
            "type": "shell",
            "command": "echo",
            "args": [
                "Right-click on HTML file and select 'Open with Live Server'"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared",
                "showReuseMessage": true,
                "clear": false
            },
            "problemMatcher": []
        },
        {
            "label": "Find Latest Analysis",
            "type": "shell",
            "command": "find",
            "args": [
                ".",
                "-name",
                "instagram_analysis.html",
                "-type",
                "f",
                "-printf",
                "%T@ %p\\n",
                "|",
                "sort",
                "-n",
                "|",
                "tail",
                "-1",
                "|",
                "cut",
                "-d' '",
                "-f2-"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
EOF

    echo "  ✅ Created VS Code tasks.json"
    echo "  💡 Use Ctrl+Shift+P -> 'Tasks: Run Task' to access these tasks"
}

# Main function
main() {
    echo "🎨 Instagram Analyzer - VS Code HTML Viewer"
    echo "=========================================="
    echo ""

    # Handle command line arguments
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Usage: $0 [file.html|--setup]"
        echo ""
        echo "Options:"
        echo "  file.html    Specific HTML file to view"
        echo "  --setup      Create VS Code tasks for HTML viewing"
        echo "  --help, -h   Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                          # Find and select analysis to view"
        echo "  $0 output/analysis.html     # View specific file"
        echo "  $0 --setup                  # Create VS Code tasks"
        echo ""
        return 0
    fi

    if [ "$1" = "--setup" ]; then
        create_vscode_tasks
        echo ""
        echo "✅ VS Code setup completed!"
        echo ""
        echo "🔧 Available extensions:"
        echo "  • Microsoft Edge Tools (ms-edgedevtools.vscode-edge-devtools)"
        echo "  • Live Server (ms-vscode.live-server)"
        echo ""
        echo "📋 How to use:"
        echo "  1. Generate analysis: poetry run python examples/analisis_personalizado.py"
        echo "  2. Find HTML file in Explorer panel"
        echo "  3. Right-click -> 'Open with Live Server'"
        echo "  4. View in VS Code's integrated browser"
        echo ""
        return 0
    fi

    local selected_file=""

    if [ -n "$1" ]; then
        # Specific file provided
        if [ -f "$1" ]; then
            selected_file="$1"
            echo "📂 Opening specified file: $1"
        else
            echo "❌ File not found: $1"
            return 1
        fi
    else
        # Search for analysis files
        local files_output=$(find_analysis_files)
        if [ $? -ne 0 ]; then
            return 1
        fi

        # Convert output to array
        local files=()
        while IFS= read -r line; do
            [ -n "$line" ] && files+=("$line")
        done <<< "$files_output"

        # Let user select file
        selected_file=$(select_file "${files[@]}")
    fi

    if [ -z "$selected_file" ]; then
        echo "❌ No file selected"
        return 1
    fi

    # Show file info
    get_file_info "$selected_file"
    echo ""

    # Open with VS Code Edge extension
    open_with_edge "$selected_file"

    echo ""
    echo "✅ Instructions provided!"
    echo ""
    echo "💡 Quick Tips:"
    echo "  • Live Server is best for interactive HTML with JavaScript"
    echo "  • Edge DevTools provides debugging capabilities"
    echo "  • VS Code Preview works for simple HTML viewing"
    echo "  • All methods work within the VS Code environment"
    echo ""
}

# Run main function with all arguments
main "$@"
