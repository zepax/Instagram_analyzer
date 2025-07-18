#!/bin/bash

# Git Automation Setup Script for Instagram Analyzer
# This script sets up git hooks and aliases for automated branch management

set -e

PROJECT_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

echo "🚀 Setting up Git Automation for Instagram Analyzer"

# Create .git/hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install git hooks
echo "📦 Installing git hooks..."

# Copy prepare-commit-msg hook
if [ -f "$SCRIPTS_DIR/git-hooks/prepare-commit-msg" ]; then
    cp "$SCRIPTS_DIR/git-hooks/prepare-commit-msg" "$HOOKS_DIR/"
    chmod +x "$HOOKS_DIR/prepare-commit-msg"
    echo "✅ Installed prepare-commit-msg hook"
else
    echo "❌ prepare-commit-msg hook not found"
fi

# Set up git aliases
echo "⚙️ Setting up git aliases..."

# Alias for creating feature branches
git config alias.feat '!f() { python scripts/git-automation.py --type feature --description "$1"; }; f'
git config alias.fix '!f() { python scripts/git-automation.py --type bugfix --description "$1"; }; f'
git config alias.perf '!f() { python scripts/git-automation.py --type optimization --description "$1"; }; f'
git config alias.docs '!f() { python scripts/git-automation.py --type documentation --description "$1"; }; f'
git config alias.test '!f() { python scripts/git-automation.py --type testing --description "$1"; }; f'
git config alias.infra '!f() { python scripts/git-automation.py --type infrastructure --description "$1"; }; f'

# Interactive branch creation
git config alias.branch-new '!python scripts/git-automation.py --interactive'

# Show branch history
git config alias.branch-history '!python scripts/git-automation.py --history'

# Smart commit with automatic versioning
git config alias.smart-commit '!f() {
    BRANCH=$(git branch --show-current)
    TYPE=$(echo "$BRANCH" | cut -d"/" -f1)
    python scripts/git-automation.py --type "$TYPE" --description "$1"
}; f'

echo "✅ Git aliases configured:"
echo "  git feat 'description'     - Create feature branch"
echo "  git fix 'description'      - Create bugfix branch"
echo "  git perf 'description'     - Create optimization branch"
echo "  git docs 'description'     - Create documentation branch"
echo "  git test 'description'     - Create testing branch"
echo "  git infra 'description'    - Create infrastructure branch"
echo "  git branch-new             - Interactive branch creation"
echo "  git branch-history         - Show branch history"

# Set up git configuration for better workflow
echo "⚙️ Configuring git workflow settings..."

# Enable automatic tracking of remote branches
git config branch.autoSetupRebase always
git config branch.autoSetupMerge always

# Set up better diff and merge tools
git config diff.algorithm histogram
git config merge.conflictStyle diff3

# Configure push behavior
git config push.default current
git config push.autoSetupRemote true

# Set up better log formatting
git config alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
git config alias.lga "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --all"

# Create initial automation config
if [ ! -f "$PROJECT_ROOT/.git-automation.json" ]; then
    echo "📝 Creating initial automation configuration..."
    cat > "$PROJECT_ROOT/.git-automation.json" << EOF
{
  "base_branch": "main",
  "auto_version": true,
  "auto_commit": false,
  "require_tests": true,
  "branch_history": [],
  "version_history": [],
  "workflow": {
    "feature_branch_pattern": "feat/{phase}-{description}-{date}",
    "commit_message_template": "{type}: {description}",
    "pr_template_enabled": true
  }
}
EOF
    echo "✅ Created .git-automation.json"
fi

# Make scripts executable
chmod +x "$SCRIPTS_DIR/git-automation.py"
chmod +x "$SCRIPTS_DIR/setup-git-automation.sh"

echo ""
echo "🎉 Git automation setup complete!"
echo ""
echo "Usage examples:"
echo "  git feat 'Add compact HTML reports'     # Creates feat/add-compact-html-reports-20250718"
echo "  git fix 'Fix story parsing bug'         # Creates fix/fix-story-parsing-bug-20250718"
echo "  git branch-new                          # Interactive branch creation"
echo "  git branch-history                      # View branch history"
echo ""
echo "The system will automatically:"
echo "  ✅ Create dated feature branches"
echo "  ✅ Format commit messages"
echo "  ✅ Increment versions based on change type"
echo "  ✅ Track branch and version history"
echo "  ✅ Follow TODO.md phase structure"
echo ""
echo "Next steps:"
echo "  1. Try: git branch-new"
echo "  2. Make your changes"
echo "  3. Commit normally - messages will be auto-formatted"
echo "  4. Create PR when ready"
