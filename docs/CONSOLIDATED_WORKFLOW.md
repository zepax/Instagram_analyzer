# Consolidated Workflow Architecture

This document explains the consolidated workflow architecture for the Instagram Analyzer project.

## Overview

The Instagram Analyzer project has moved from multiple separate workflows to a single consolidated workflow that integrates:
- CI/CD pipeline functionality
- ML pipeline automation
- Multi-agent AI system

This consolidation provides several benefits:
- Reduced duplication of configuration and code
- Clearer workflow visualization
- Easier maintenance and updates
- Better integration between systems

## Workflow Structure

The main workflow is defined in `.github/workflows/main-workflow.yml` and consists of the following jobs:

1. **Triage**: Analyzes issues and PRs, assigns appropriate AI agents
2. **Testing**: Runs unit and integration tests across multiple Python versions
3. **Security**: Performs security scanning and vulnerability analysis
4. **Type-Check**: Verifies Python type annotations using MyPy
5. **ML Pipeline**: Executes machine learning training pipeline
6. **Documentation**: Generates and deploys project documentation
7. **Build**: Creates Python package artifacts
8. **AI Review**: AI agent for code review and static analysis
9. **AI Documentation**: AI agent for documentation improvements
10. **Additional AI Agents**: Optimization, Testing, and Feature agents

## Triggers

The workflow is triggered by:
- **Push events** to any branch affecting source code or workflow files
- **Pull requests** to any branch affecting source code
- **Issues** that are opened, edited, or labeled
- **Manual dispatch** with customizable inputs

## AI Agent Integration

The consolidated workflow includes the AI agent system that was previously spread across multiple workflows. The main workflow handles:

1. **Orchestration**: Assigning tasks based on labels or content analysis
2. **Agent Execution**: Running specialized AI agents when needed
3. **Reporting**: Generating insights and comments on issues/PRs

## Configuration

The workflow can be customized through:
- **GitHub Secrets**: For API keys and tokens
- **Manual triggers**: For specific task execution
- **Issues/PR labels**: For directing specific agent tasks

## Migration from Previous Workflows

This consolidated workflow replaces:
- `ci.yml`: CI/CD pipeline
- `ml-pipeline-docs.yml`: ML pipeline and documentation
- Individual AI agent workflows are now integrated (but still available for direct execution)

## Future Expansion

The consolidated architecture makes it easier to:
- Add new AI agents
- Enhance existing workflow steps
- Create pipeline dependencies
- Track workflow execution status
