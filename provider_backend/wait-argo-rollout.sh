#!/bin/sh

set -o pipefail
attempts=900
timedout=1

for i in `seq $attempts`; do
    echo "waiting for argo rollout to complete deployment: $i/$attempts"
    kubectl --namespace "$CITY" get rollouts.argoproj.io "$CITY" -o json | jq ".status.stableRS == .status.currentPodHash" --exit-status > /dev/null
    if [ $? -eq 0 ]; then
        timedout=0
        break
    fi

    kubectl --namespace "$CITY" get rollouts.argoproj.io "$CITY" -o json | jq ".status.abort == true" --exit-status > /dev/null
    if [ $? -eq 0 ]; then
        timedout=0
        break
    fi

    sleep 1
done

if [ $timedout -ne 0 ]; then
    echo "Deployment timed out"
    exit 1
fi

kubectl --namespace "$CITY" get rollouts.argoproj.io "$CITY" -o json | jq ".status.abort == null" --exit-status > /dev/null
if [ $? -eq 0 ]; then
    echo "Deployment successfull"
    exit 0
fi

echo "Deployment failed"
exit 1
