#!/bin/bash

# Instagram Analyzer Viewer
# Script to easily view HTML analysis reports with Microsoft Edge

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

# Function to check if GUI is running
check_gui() {
    if ! pgrep -f "Xvfb" > /dev/null; then
        echo "⚠️  GUI services not running. Starting them now..."
        /workspaces/Instagram_analyzer/.devcontainer/start-gui.sh start
        echo ""

        # Wait a moment for services to start
        sleep 3

        if ! pgrep -f "Xvfb" > /dev/null; then
            echo "❌ Failed to start GUI services"
            return 1
        fi
    fi
    return 0
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

# Main function
main() {
    echo "🎨 Instagram Analyzer Viewer"
    echo "================================"
    echo ""

    # Handle command line arguments
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Usage: $0 [file.html]"
        echo ""
        echo "Options:"
        echo "  file.html    Specific HTML file to open"
        echo "  --help, -h   Show this help message"
        echo ""
        echo "If no file is specified, the script will search for analysis files."
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

    # Get absolute path
    selected_file=$(realpath "$selected_file")

    # Show file info
    get_file_info "$selected_file"
    echo ""

    # Check and start GUI if needed
    if ! check_gui; then
        return 1
    fi

    # Open the file
    echo "🌐 Opening in Microsoft Edge..."
    /workspaces/Instagram_analyzer/.devcontainer/start-gui.sh open "$selected_file"

    echo ""
    echo "✅ File opened successfully!"
    echo ""
    echo "💡 Tips:"
    echo "  • Use gui-status to check if services are running"
    echo "  • Use stop-gui to stop all GUI services"
    echo "  • The file will open in a virtual display accessible via VNC"
    echo ""
}

# Run main function with all arguments
main "$@"
