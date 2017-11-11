#!/bin/bash

PROFILE=$1

if [ -z "$PROFILE" ]; then
  echo "Missing first argument PROFILE. It's the AWS profile you want to use for deploying."
  exit 0
fi

aws s3 cp output/hy_courses.json s3://kurssim.me \
  --region eu-central-1 \
  --acl public-read \
  --cache-control max-age=3600 \
  --profile $PROFILE