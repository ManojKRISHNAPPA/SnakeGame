#!/bin/bash

echo "authentication with snyk"
snyk auth "$SNYK_TOKEN"

echo "succesfuly authenticated..."

echo "Running snyk test"

snyk iac test . --severity-threshold=critical || {
    echo "Critical vulnarabilties found please check the code"
    exit 1
}

echo "No critical vulnarabilties found"