# Signal

An autonomous agent that watches for new information, remembers what it has already reported, drafts a briefing, critiques its own draft, and reports back — without any human triggering each run.

Built for the AWS Builder Center "Build an Always-On Agent" Weekend Challenge.

---

## 📌 Overview

**Signal** is an autonomous AI agent built for the **AWS Weekend Agent Challenge**.

Instead of waiting for a user to click a button, Signal runs **unattended** on a schedule or in response to an event.

Every execution performs the following workflow:

- Fetches the latest Hacker News stories
- Remembers stories already reported
- Filters out duplicates
- Uses Amazon Bedrock (Nova Micro) to generate an AI morning briefing
- Reviews and improves its own draft using a second AI pass
- Sends the final report via Amazon SES
- Stores execution history for future runs

The result is an intelligent daily briefing system that continuously works in the background.

---
---

# ✨ Features

- 🤖 Fully autonomous AI agent
- 🧠 Persistent memory using DynamoDB
- 📰 Fetches live Hacker News stories
- 🚫 Avoids duplicate reporting
- ✍️ AI-generated summaries using Amazon Nova Micro
- 🔍 Self-critiques and improves generated content
- 📧 Sends email briefings automatically
- ⏰ Scheduled execution using EventBridge
- ⚡ Event-driven execution using Amazon S3
- ☁️ Completely serverless architecture

---

## Architecture

```
EventBridge (daily 6AM) ─┐
EventBridge (hourly)  ───┼──► Lambda: signal-agent ──► Bedrock (draft + self-critique)
S3 event (file upload) ──┘                          ──► SES (email)
                                                      ──► DynamoDB (memory + run log)
                                                              │
                                                              ▼
                                          Lambda: signal-dashboard-api
                                                              │
                                                              ▼
                                              API Gateway (HTTP API)
                                                              │
                                                              ▼
                                       S3 static site (public dashboard)
```

---

# ☁ AWS Services Used

| Service | Purpose |
|----------|---------|
| AWS Lambda | Executes the autonomous agent |
| Amazon Bedrock | AI reasoning and summarization |
| Amazon Nova Micro | LLM used for report generation |
| Amazon DynamoDB | Persistent memory of reported stories |
| Amazon SES | Sends the generated email |
| Amazon EventBridge Scheduler | Daily unattended execution |
| Amazon S3 | Event-based trigger |
| Amazon CloudWatch | Monitoring and logs |
| IAM | Secure permissions |

---


## Files
- `lambda_function.py` — main agent: fetch → filter unseen → plan/draft (Bedrock) → self-critique (Bedrock) → email (SES) → log (DynamoDB). Also handles hourly "watcher" mode for anomaly alerts.
- `dashboard/dashboard_api.py` — Lambda backing the public dashboard's `/runs` and `/feedback` API routes.
- `dashboard/index.html` — static dashboard page, hosted on S3, showing live run history.
- `screenshots/` — proof of unattended operation (see below).

## Live Dashboard
http://signal-agent-dashboard-rebeccavio12262.s3-website-us-east-1.amazonaws.com/

## Video Walkthrough
https://drive.google.com/file/d/14BRrJJK4YxDxJZsOCxefY-trffHeMfx2/view?usp=sharing

# 📸 Screenshots

Below are screenshots demonstrating the architecture, deployment, autonomous execution, and successful operation of the Signal AI Agent.

1. **1BEDROCK.png** — Amazon Bedrock model access showing Amazon Nova models enabled for the project.

2. **3DYNAMODB.png** — DynamoDB table (`signal-agent-memory`) used by the agent to remember previously processed stories and execution history.

3. **4DYNAMODBITEMS.png** — Items stored in DynamoDB, demonstrating persistent memory and preventing duplicate story reports.

4. **5S3.png** — Amazon S3 bucket configured as an event source for the Lambda function.

5. **6LAMBDA.png** — AWS Lambda function overview showing the deployed autonomous Signal Agent.

6. **7LAMBDACONFIG.png** — Lambda configuration, including environment variables used by the application.

7. **8LAMBDACODE.png** — Lambda source code implementing the autonomous AI workflow.

8. **10CLOUDWATCH.png** — Amazon CloudWatch logs showing successful Lambda executions and monitoring information.

9. **11EVENTBRIDGE.png** — Amazon EventBridge Scheduler configured to automatically trigger the agent without human interaction.

10. **13EMAIL.png** — Example AI-generated morning briefing delivered through Amazon Simple Email Service (SES).

11. **14DASHBOARD.png** — Public web dashboard displaying the latest AI-generated brief and application status.

12. **15api.png** — Amazon API Gateway configuration exposing REST endpoints used by the dashboard.

---


---

# 📸 Demonstration

The repository includes screenshots demonstrating:

- ✅ Bedrock Model Access
- ✅ Lambda Deployment
- ✅ Environment Variables
- ✅ Successful Lambda Execution
- ✅ CloudWatch Logs
- ✅ DynamoDB Memory
- ✅ EventBridge Scheduler
- ✅ Amazon S3 Trigger
- ✅ Generated Email
- ✅ Autonomous Execution

---
---

# 🔐 Security

- IAM roles follow least-privilege principles for the hackathon environment.
- Secrets are stored using Lambda environment variables.
- Email sending is restricted to verified identities in Amazon SES.

---

# 📈 Future Improvements

- User preferences
- Multiple news sources
- Slack / Discord notifications
- Daily digest personalization
- RSS feed support
- Web dashboard
- Sentiment analysis
- Multi-agent collaboration
- Vector database memory
- Amazon Bedrock Knowledge Bases

---

# 🎯 Challenge Requirements

✅ Autonomous AI agent

✅ Runs unattended

✅ Triggered automatically

✅ Reports results back

✅ Uses AWS services

✅ AI-powered reasoning

---
## ⭐ If you found this project interesting, consider giving it a star!