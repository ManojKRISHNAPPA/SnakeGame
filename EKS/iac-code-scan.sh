#!/bin/bash
set -e

echo "Running Snyk IaC Scan..."

SNYK_TOKEN="ca119e6e-bfe8-4c39-a29c-38575377963c"

snyk auth $SNYK_TOKEN


if snyk iac test --severity-threshold=critical; then
    echo "✅ No critical vulnerabilities found"
else
    echo "❌ Critical vulnerabilities detected"
    exit 1
fi