import os, json, decimal, boto3
from boto3.dynamodb.conditions import Attr

TABLE = os.environ["DYNAMO_TABLE"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE)


def decimal_default(o):
    if isinstance(o, decimal.Decimal):
        return int(o)
    raise TypeError


def cors(body, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": json.dumps(body, default=decimal_default)
    }


def handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("rawPath", "/")

    if method == "OPTIONS":
        return cors({})

    if path == "/runs" and method == "GET":
        resp = table.scan(FilterExpression=Attr("story_id").begins_with("RUN#"))
        items = sorted(resp["Items"], key=lambda x: x["story_id"], reverse=True)[:20]
        return cors(items)

    if path == "/feedback" and method == "POST":
        body = json.loads(event.get("body", "{}"))
        story_id = body.get("story_id")
        vote = body.get("vote")
        title = body.get("title", "")
        table.put_item(Item={"story_id": f"FEEDBACK#{story_id}", "vote": vote, "title": title})
        return cors({"status": "recorded"})

    return cors({"error": "not found"}, 404)
