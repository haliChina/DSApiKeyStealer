# DeepSeek API Key Leak Checker

<p align="center">
  <a href="./README.md">简体中文 Version</a>
</p>

## Note:
This method is publicly applicable. If you insist on thinking that I am mass-scanning your API keys and feel the need to send an abuse report to GitHub, all I can say is you need to open your eyes.
> This tool is intended **solely for legal security research and educational purposes**. Please delete it within **24 hours** after downloading.
> Pay attention to this statement: This tool is fundamentally for exchange and learning. I have never collected other users' information, nor have I ever allowed others to use this tool for unauthorized scanning.

### @chinese-leak-key-check's activity is private
The method has been patched/fixed.

## ⚠️ Disclaimer
> This tool is intended **solely for legal security research and educational purposes**. Please delete it within **24 hours** after downloading.

## Regarding Trae's contribution:
Trae's contribution happened because ByteDance went crazy. I customized my model to GPT-5.

## FAQ (Frequently Asked Questions)

### Where do I get a Token?
Go to:
Select "classic" and check the scopes/permissions you need

### Issue: Everything returns all zeros (0)
**Answer:** You didn't add the environment variable.
```env
GITHUB_TOKEN=xxx

```
Alternatively, you can replace that block of code with:
```Python
"ghp_xxxxxxxxxxxxxxxxxxxx"

```

### Other issues:
Open an Issue.

## Legal Notice
> By using this tool, you agree to the following terms:

### Authorized Use Only
This tool is designed for security researchers to detect and confirm API Key leakage issues. You may only scan repositories/files that you own or have received explicit written authorization to test.
Unauthorized scanning of others' repositories may violate the Computer Fraud and Abuse Act (CFAA), GDPR, the Cybersecurity Law of the People's Republic of China, and other applicable legislation.

### Prohibited Uses:
 * ❌ Unauthorized access to others' accounts or resources.
 * ❌ Utilizing leaked API Keys belonging to others for any operation.
 * ❌ Using this tool for malicious purposes or illegal activities.
 * ❌ Testing on unauthorized systems.

### Please Note:
 * Your use of this tool is strictly at your own risk.
 * The author assumes no liability or responsibility for any misuse or abuse.
 * Using leaked credentials belonging to others may violate criminal laws.

### Liability Disclaimer:
This tool is provided "as is", without warranty of any kind, express or implied.
The user assumes full responsibility for any legal consequences, data breaches, or asset losses resulting from the use of this tool.

### Remediation upon discovering a real leak:
If you discover a genuine key leak:
 * Privately notify the repository owner.
 * Advise them to immediately revoke/rotate the key.
 * Do NOT include any plaintext key content in public issues or PRs.
 * Adhere to responsible disclosure practices.
   This is not an exploit tool.

### This tool is intended solely for defensive security research and authorized penetration testing.
For commercial service keys (OpenAI, Anthropic, DeepSeek, etc.), please comply with each respective platform's Terms of Service.

### Friendly Reminder:
 * Report leaked keys responsibly if you find them.
 * Never use resources belonging to others, regardless of whether they are "valid" or not.
 * Please conduct security testing in a controlled environment.

If you do not agree to the terms above, please cease using this tool immediately and delete all related files.
---
**By using this tool, you signify your agreement to the above terms.**
