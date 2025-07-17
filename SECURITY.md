# Security Policy

## Supported Versions

We actively support the following versions of Instagram Analyzer with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within Instagram Analyzer, please send an email to the project maintainers. All security vulnerabilities will be promptly addressed.

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include

When reporting a vulnerability, please include:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Affected versions**
4. **Potential impact** assessment
5. **Suggested fix** (if you have one)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Detailed Response**: Within 7 days
- **Fix Timeline**: Critical issues within 30 days

### Security Measures

Instagram Analyzer implements several security measures:

- **Input Validation**: All user inputs are validated and sanitized
- **Dependency Scanning**: Regular security scanning with `bandit` and `safety`
- **Code Analysis**: Static analysis tools to detect potential vulnerabilities
- **Secure Defaults**: Secure configuration defaults
- **Data Privacy**: Local processing only, no external data transmission

### Security Best Practices for Users

1. **Keep Updated**: Always use the latest version
2. **Review Data**: Be careful when sharing generated reports
3. **Environment Security**: Secure your development environment
4. **Dependencies**: Keep Python and dependencies updated
5. **Access Control**: Limit access to sensitive Instagram data

## Security Contact

For security-related questions or concerns, please contact:
- Email: [maintainer-email@example.com]
- GPG Key: [if applicable]

Thank you for helping keep Instagram Analyzer secure!
