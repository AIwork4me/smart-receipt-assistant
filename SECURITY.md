# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of Smart Receipt Assistant seriously. If you have discovered a security vulnerability, we appreciate your help in disclosing it to us in a responsible manner.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them by:

1. **Email**: Send details to the project maintainers via GitHub
2. **GitHub Security**: Use the [Security Advisories](https://github.com/AIwork4me/smart-receipt-assistant/security/advisories) feature

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., buffer overflow, SQL injection, cross-site scripting)
- Full paths of source file(s) related to the vulnerability
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution**: Depends on severity, typically within 30 days

### Disclosure Policy

- We will confirm the vulnerability and determine its impact
- We will release a fix as soon as possible
- We will publicly disclose the issue after the fix is released
- We will credit the reporter (unless they prefer to remain anonymous)

## Security Best Practices

When using Smart Receipt Assistant:

### API Keys

- **Never commit API keys** to version control
- Use environment variables via `.env` file
- Add `.env` to `.gitignore`
- Rotate keys if they may have been exposed

### File Handling

- The application processes uploaded files (images, PDFs)
- Validate file types and sizes before processing
- Be cautious with files from untrusted sources

### Data Privacy

- Receipt data may contain sensitive financial information
- Ensure proper handling and storage of processed data
- Follow your organization's data protection policies

## Security Features

This project includes:

- **Environment variable configuration** for sensitive data
- **Input validation** via Pydantic models
- **Type checking** with mypy
- **Dependency scanning** via GitHub Dependabot

## Known Security Considerations

### Third-Party Services

This application uses external APIs:

1. **PaddleOCR API**: Files are sent to PaddleOCR servers for OCR processing
2. **ERINE API**: Text is sent to Baidu AIStudio for LLM processing

**Important**: Review the privacy policies of these services before processing sensitive documents.

### Recommendations

- For highly sensitive documents, consider self-hosted OCR solutions
- Implement data retention policies for processed receipts
- Use network security measures (VPN, firewalls) as appropriate

## Updates

Security updates will be announced via:

- GitHub Releases
- GitHub Security Advisories

We recommend watching the repository for security updates.

---

Thank you for helping keep Smart Receipt Assistant secure! 🔐
