// Agent Results Aggregation Script
// This script consolidates results from all specialized agents
// Used by the AI Orchestrator workflow

const fs = require('fs').promises;
const core = require('@actions/core');

async function run() {
  try {
    // Get issue/PR number
    const issueNumber = process.env.GITHUB_CONTEXT_ISSUE 
      ? JSON.parse(process.env.GITHUB_CONTEXT_ISSUE).number
      : (process.env.GITHUB_CONTEXT_PR ? JSON.parse(process.env.GITHUB_CONTEXT_PR).number : null);
    
    if (!issueNumber) {
      console.log('No issue/PR to update');
      return;
    }
    
    // Get assigned labels from env
    const labels = process.env.ASSIGNED_LABELS ? process.env.ASSIGNED_LABELS.split(',') : [];
    
    // Read shared context for agent results (simulated for now)
    let agentResults = {};
    try {
      const contextPath = '.task-context/context.json';
      const contextContent = await fs.readFile(contextPath, 'utf8');
      const contextData = JSON.parse(contextContent);
      agentResults = contextData.agent_results || {};
    } catch (error) {
      console.error(`Error reading agent results from context: ${error}`);
      // In a real case, we would handle this (e.g., show an error message in the comment)
    }
    
    // Create results summary
    let summary = `## 🤖 Multi-Agent Task Summary\n\n`;
    summary += `**Orchestrator ID**: \`${process.env.GITHUB_RUN_ID}\`\n`;
    summary += `**Context Key**: \`${process.env.CONTEXT_KEY}\`\n`;
    summary += `**Assigned Labels**: ${process.env.ASSIGNED_LABELS}\n\n`;
    
    // Add status of activated agents
    summary += `### Activated Agents:\n`;
    
    if (labels.includes('ai:docs')) {
      summary += `- 📚 **Documentation Agent**: Processing documentation updates\n`;
      if (agentResults['ai-documentation-agent.yml'] && agentResults['ai-documentation-agent.yml'].pr_number) {
        summary += `  - Created PR: #${agentResults['ai-documentation-agent.yml'].pr_number}\n`;
      }
    }
    if (labels.includes('ai:test')) {
      summary += `- 🧪 **Testing Agent**: Implementing tests\n`;
      if (agentResults['ai-testing-agent.yml'] && agentResults['ai-testing-agent.yml'].pr_number) {
        summary += `  - Created PR: #${agentResults['ai-testing-agent.yml'].pr_number}\n`;
      }
    }
    if (labels.includes('ai:optimize')) {
      summary += `- ⚡ **Optimization Agent**: Analyzing performance\n`;
      if (agentResults['ai-optimization-agent.yml'] && agentResults['ai-optimization-agent.yml'].report_path) {
        summary += `  - Report available at: ${agentResults['ai-optimization-agent.yml'].report_path}\n`;
      }
    }
    if (labels.includes('ai:feature')) {
      summary += `- 🚀 **Feature Agent**: Developing new functionality\n`;
      if (agentResults['ai-feature-agent.yml'] && agentResults['ai-feature-agent.yml'].pr_number) {
        summary += `  - Created PR: #${agentResults['ai-feature-agent.yml'].pr_number}\n`;
      }
    }
    if (labels.includes('ai:review')) {
      summary += `- 👁️ **Review Agent**: Conducting code review\n`;
      if (agentResults['ai-review-agent.yml'] && agentResults['ai-review-agent.yml'].report_url) {
        summary += `  - Review report: ${agentResults['ai-review-agent.yml'].report_url}\n`;
      }
    }
    if (labels.includes('ai:security')) {
      summary += `- 🔒 **Security Agent**: Analyzing security vulnerabilities\n`;
      if (agentResults['ai-security-agent.yml'] && agentResults['ai-security-agent.yml'].report_path) {
        summary += `  - Report available at: ${agentResults['ai-security-agent.yml'].report_path}\n`;
      }
    }
    
    // Generic messages
    summary += `\n### Next Steps:\n`;
    summary += `- Specialized agents will create detailed analysis and PRs\n`;
    summary += `- Track progress in the [Actions tab](https://github.com/${process.env.GITHUB_REPOSITORY}/actions)\n`;
    summary += `- Agent results will be updated in this issue\n\n`;
    summary += `*Orchestrated by Multi-Agent System v2.0*`;
    
    // Output the summary to be used in the GitHub Action
    core.setOutput('summary', summary);
    
    // In the actual action, we would use the GitHub API to post this comment
    console.log('Summary prepared for posting');
    
  } catch (error) {
    console.error(`Error in aggregate-results script: ${error.message}`);
    core.setFailed(error.message);
  }
}

run();
