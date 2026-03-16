#!/bin/bash

dockerImageName=$(grep -m1 '^FROM' Dockerfile | awk '{print $2}')

if [[ -z "$dockerImageName" ]]; then
    echo "Error: Docker image name not found in Dockerfile."
    exit 1
fi
echo "Scanning image: $dockerImageName"

# High severity scan
trivy image --exit-code 0 --severity HIGH $dockerImageName

# Critical severity scan (fail if found)
trivy image --exit-code 1 --severity CRITICAL $dockerImageName

exit_code=$?
echo "Exit Code : $exit_code"

if [[ "${exit_code}" == 1 ]]; then
    echo "Image scanning failed. Vulnerabilities found"
    exit 1
else
    echo "Image scanning passed. No CRITICAL vulnerabilities found"
fi