#!/usr/bin/env python3
"""Generate icons for Data IESB / Aurya using Bedrock Nova Canvas.
Uploads directly to S3.
"""
import base64
import json
import boto3

ICONS = {
    "educacao":    "Graduation cap",
    "saude":       "Medical cross with heartbeat line",
    "demografia":  "Three human silhouettes group",
    "economia":    "Rising bar chart with coin",
    "governo":     "Classical government building with columns",
    "territorio":  "Globe with latitude longitude lines",
}

BASE_PROMPT = (
    "Minimalist grayscale icon, {desc}, white lines on transparent dark background, "
    "simple thin line art, monochrome, no color, no shading, no gradients, "
    "single clean outline drawing, black and white only, icon style, centered"
)

bedrock = boto3.Session(profile_name="iesb").client("bedrock-runtime", region_name="us-east-1")
s3 = boto3.Session(profile_name="iesb").client("s3", region_name="us-east-1")

BUCKET = "aurya.dataiesb.com"
PREFIX = "icons/"

for name, desc in ICONS.items():
    prompt = BASE_PROMPT.format(desc=desc)
    print(f"Generating {name}...", end=" ", flush=True)

    resp = bedrock.invoke_model(
        modelId="amazon.nova-canvas-v1:0",
        body=json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {"numberOfImages": 1, "height": 320, "width": 320},
        }),
    )
    img = base64.b64decode(json.loads(resp["body"].read())["images"][0])

    key = f"{PREFIX}{name}.png"
    s3.put_object(Bucket=BUCKET, Key=key, Body=img, ContentType="image/png")
    print(f"↑ s3://{BUCKET}/{key}")

print(f"\n✅ {len(ICONS)} icons generated and uploaded.")
