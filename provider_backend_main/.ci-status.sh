#!/bin/bash
set -xe

if [ -z "$TG_WM_BOT_TOKEN_ID" ] || [ -z "$TG_WM_BOT_TOKEN_BODY" ] || [ -z "$TG_WM_CHAT_ID" ]; then
  exit 0
fi

set -o nounset

success=$1                      # 1 or 0 (success and failure)
status=$2                       # arbitrary string

if (( success )); then
    symbol=✅
else
    symbol=❌
fi

URL="https://api.telegram.org/bot${TG_WM_BOT_TOKEN_ID}:${TG_WM_BOT_TOKEN_BODY}/sendMessage"
TEXT="${symbol} ${status} pipeline on ${CI_PROJECT_NAME}/${CI_COMMIT_REF_SLUG}%0A%0AURL:+$CI_PROJECT_URL/pipelines/$CI_PIPELINE_ID/%0AUsername:+$GITLAB_USER_NAME"
curl -sv --max-time 10 -d "chat_id=${TG_WM_CHAT_ID}&disable_web_page_preview=1&text=${TEXT}" "$URL" > /dev/null
