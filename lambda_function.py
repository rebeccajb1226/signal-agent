import os, json, time, urllib.request
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Attr

TABLE = os.environ["DYNAMO_TABLE"]
SENDER = os.environ["SENDER_EMAIL"]
RECIPIENT = os.environ["RECIPIENT_EMAIL"]
MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-micro-v1:0")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE)
bedrock = boto3.client("bedrock-runtime")
ses = boto3.client("ses")


def fetch_top_stories(n=15):
    with urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json") as r:
        ids = json.loads(r.read())[:n]
    stories = []
    for sid in ids:
        with urllib.request.urlopen(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json") as r:
            item = json.loads(r.read())
            if item and item.get("title"):
                stories.append({"id": sid, "title": item["title"], "url": item.get("url", ""), "score": item.get("score", 0)})
    return stories


def filter_unseen(stories):
    unseen = []
    for s in stories:
        resp = table.get_item(Key={"story_id": str(s["id"])})
        if "Item" not in resp:
            unseen.append(s)
    return unseen


def call_bedrock(prompt):
    resp = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 500, "temperature": 0.4}
    )
    return resp["output"]["message"]["content"][0]["text"]


def plan_and_draft(stories):
    story_list = "\n".join(f"- {s['title']} (score {s['score']}) {s['url']}" for s in stories)
    prompt = ("You are an autonomous morning briefing agent. Below are new Hacker News stories "
              "the user hasn't seen yet. Pick the 5 most interesting/important ones and write a short, "
              "friendly morning brief summarizing why each matters. Keep it concise.\n\n" + story_list)
    return call_bedrock(prompt)


def self_critique(draft):
    prompt = ("Review this morning brief draft for accuracy, redundancy, and clarity. "
              "Rewrite it if needed to make it tighter and more useful. Return only the final version.\n\n" + draft)
    return call_bedrock(prompt)


def send_email(body, trigger_source, subject_prefix="Signal Morning Brief"):
    subject = f"{subject_prefix} - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    full_body = f"(Triggered by: {trigger_source})\n\n{body}"
    ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses": [RECIPIENT]},
        Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": full_body}}}
    )


def log_run(stories, final, trigger_source):
    table.put_item(Item={
        "story_id": f"RUN#{int(time.time())}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trigger_source": trigger_source,
        "num_stories": len(stories),
        "final_brief": final[:2000]
    })
    for s in stories:
        table.put_item(Item={"story_id": str(s["id"]), "title": s["title"],
                              "reported_at": datetime.now(timezone.utc).isoformat()})


def watcher_check():
    stories = fetch_top_stories(n=30)
    alerts = []
    for s in stories:
        resp = table.get_item(Key={"story_id": f"WATCH#{s['id']}"})
        prev_score = resp.get("Item", {}).get("score", 0)
        if s["score"] - prev_score >= 150:
            alerts.append(s)
        table.put_item(Item={"story_id": f"WATCH#{s['id']}", "score": s["score"]})
    if alerts:
        body = "\n".join(f"Alert: '{a['title']}' jumped to {a['score']} points - {a['url']}" for a in alerts)
        send_email(body, "watcher-schedule", subject_prefix="Signal Watcher Alert")
    return {"status": "watched", "alerts": len(alerts)}


def handler(event, context):
    if event.get("mode") == "watch":
        return watcher_check()

    trigger_source = "s3-event" if "Records" in event else "schedule/manual"
    stories = fetch_top_stories()
    unseen = filter_unseen(stories)
    if not unseen:
        return {"status": "no new stories"}
    draft = plan_and_draft(unseen)
    final = self_critique(draft)
    send_email(final, trigger_source)
    log_run(unseen, final, trigger_source)
    return {"status": "ok", "reported": len(unseen)}
