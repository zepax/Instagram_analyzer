#!/bin/bash

# Instagram Analyzer Demo
# This script demonstrates the full workflow from analysis generation to visualization

echo "🎨 Instagram Analyzer - Full Demo"
echo "=================================="
echo ""

# Function to check if Poetry is available
check_poetry() {
    if ! command -v poetry &> /dev/null; then
        echo "❌ Poetry not found. Please install Poetry first."
        return 1
    fi
    echo "✅ Poetry found"
}

# Function to check if project is properly installed
check_installation() {
    echo "🔍 Checking project installation..."
    if poetry run python -c "import src.instagram_analyzer; print('✅ Project imports working')" 2>/dev/null; then
        return 0
    else
        echo "⚠️  Project not properly installed. Installing now..."
        poetry install --with dev
        return $?
    fi
}

# Function to check for sample data
check_sample_data() {
    echo "📁 Checking for sample data..."

    # Look for any JSON files that might be Instagram data
    local data_files=(
        "data/sample_exports/"*.json
        "test_data/"*.json
        "*instagram*.json"
        "*posts*.json"
        "*messages*.json"
        "*stories*.json"
    )

    local found_data=false
    for pattern in "${data_files[@]}"; do
        if ls $pattern 2>/dev/null | head -1 >/dev/null; then
            echo "  ✅ Found data files matching: $pattern"
            found_data=true
        fi
    done

    if [ "$found_data" = false ]; then
        echo "  ⚠️  No Instagram data files found"
        echo "  💡 Please add your Instagram export data to the project"
        echo ""
        echo "  Expected file structure:"
        echo "    posts/posts_1.json"
        echo "    messages/inbox/*/message_1.json"
        echo "    stories/stories.json"
        echo "    liked_posts.json"
        echo "    post_comments.json"
        echo ""
        return 1
    fi

    return 0
}

# Function to run analysis
run_analysis() {
    local output_dir="${1:-demo_output}"

    echo "🧠 Running Instagram analysis..."
    echo "Output directory: $output_dir"
    echo ""

    # Create output directory
    mkdir -p "$output_dir"

    # Check if the analysis example exists
    if [ -f "examples/analisis_personalizado.py" ]; then
        echo "📊 Using custom analysis script..."

        # Run the analysis with output redirection
        if poetry run python examples/analisis_personalizado.py > "$output_dir/analysis.log" 2>&1; then
            echo "✅ Analysis completed successfully"

            # Check if HTML was generated
            if [ -f "output/instagram_analysis.html" ]; then
                # Copy to demo output directory
                cp output/instagram_analysis.html "$output_dir/"
                echo "📄 HTML report generated: $output_dir/instagram_analysis.html"
                return 0
            else
                echo "⚠️  Analysis ran but no HTML report found in output/"
                # Look for HTML files in other locations
                local html_files=($(find . -name "instagram_analysis.html" -type f 2>/dev/null | head -5))
                if [ ${#html_files[@]} -gt 0 ]; then
                    echo "📄 Found HTML report at: ${html_files[0]}"
                    cp "${html_files[0]}" "$output_dir/"
                    return 0
                fi
                return 1
            fi
        else
            echo "❌ Analysis failed. Check log: $output_dir/analysis.log"
            return 1
        fi
    else
        echo "❌ Analysis script not found: examples/analisis_personalizado.py"
        return 1
    fi
}

# Function to start GUI and show the report
show_report() {
    local output_dir="$1"
    local html_file="$output_dir/instagram_analysis.html"

    if [ ! -f "$html_file" ]; then
        echo "❌ HTML report not found: $html_file"
        return 1
    fi

    echo "🖥️  Starting GUI services..."

    # Start GUI if not already running
    if ! pgrep -f "Xvfb" > /dev/null; then
        .devcontainer/start-gui.sh start
        echo ""

        # Wait for services to be ready
        echo "⏱️  Waiting for services to start..."
        sleep 5
    else
        echo "✅ GUI services already running"
    fi

    # Check GUI status
    .devcontainer/start-gui.sh status
    echo ""

    # Open the HTML file
    echo "🌐 Opening HTML report in Microsoft Edge..."
    .devcontainer/start-gui.sh open "$html_file"

    echo ""
    echo "🎉 Demo completed successfully!"
    echo ""
    echo "📋 What happened:"
    echo "  1. ✅ Verified project installation"
    echo "  2. ✅ Generated Instagram analysis"
    echo "  3. ✅ Started GUI services (Xvfb, VNC, noVNC, Fluxbox)"
    echo "  4. ✅ Opened report in Microsoft Edge"
    echo ""
    echo "🌐 Access the report:"
    echo "  • Web VNC: http://localhost:6080/vnc.html"
    echo "  • Direct VNC: localhost:5900"
    echo "  • Local file: $(realpath $html_file)"
    echo ""
    echo "🛠️  Useful commands:"
    echo "  gui-status     - Check GUI service status"
    echo "  view-analysis  - Quick analysis viewer"
    echo "  stop-gui       - Stop all GUI services"
    echo ""
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --output, -o DIR    Output directory (default: demo_output)"
    echo "  --no-gui           Skip GUI setup and just run analysis"
    echo "  --help, -h         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Run full demo with default output"
    echo "  $0 -o my_demo         # Run demo with custom output directory"
    echo "  $0 --no-gui           # Just run analysis, no GUI"
    echo ""
}

# Parse command line arguments
output_dir="demo_output"
skip_gui=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --output|-o)
            output_dir="$2"
            shift 2
            ;;
        --no-gui)
            skip_gui=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    # Check prerequisites
    check_poetry || exit 1
    check_installation || exit 1
    check_sample_data || echo "⚠️  Continuing without sample data verification..."

    echo ""

    # Run analysis
    if run_analysis "$output_dir"; then
        echo "✅ Analysis phase completed"
    else
        echo "❌ Analysis phase failed"
        exit 1
    fi

    echo ""

    # Show report (unless --no-gui)
    if [ "$skip_gui" = false ]; then
        show_report "$output_dir"
    else
        echo "🔍 Analysis completed. Report available at: $output_dir/instagram_analysis.html"
        echo "💡 Use 'view-analysis $output_dir' to view with GUI later"
    fi
}

# Run main function
main
