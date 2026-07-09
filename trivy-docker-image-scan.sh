#!/bin/bash

dockerImageName=$(cat Dockerfile | grep "^FROM" | awk '{print $2}')

if [ -z "$dockerImageName" ]; then
  echo "No docker image name found in Dockerfile"
  exit 1
fi

echo "Scanning docker image: $dockerImageName"

# high image scan
trivy image  --exit-code 0 --severity HIGH $dockerImageName


# critical image scan
trivy image  --exit-code 1 --severity CRITICAL $dockerImageName 

exit_cde=$?
echo "trivy scan exit code: $exit_cde"

if [ $exit_cde -eq 1 ]; then
  echo "Critical vulnerabilities found in docker image: $dockerImageName"
  exit 1
else
  echo "No critical vulnerabilities found in docker image: $dockerImageName"
fi