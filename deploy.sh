#!/bin/bash
aws s3 sync static/ s3://aurya.dataiesb.com/ --delete
echo "✅ Deployed to http://aurya.dataiesb.com.s3-website-us-east-1.amazonaws.com/"
