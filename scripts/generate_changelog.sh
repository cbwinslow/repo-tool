#!/bin/bash

# Script to generate changelog from git commits
# Usage: ./generate_changelog.sh [from_tag] [to_tag]

set -e

# Configuration
CHANGELOG_FILE="CHANGELOG.md"
FROM_TAG="$1"
TO_TAG="$2"

if [ -z "$FROM_TAG" ]; then
    FROM_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [ -z "$FROM_TAG" ]; then
        FROM_TAG=$(git rev-list --max-parents=0 HEAD)
    fi
fi

if [ -z "$TO_TAG" ]; then
    TO_TAG="HEAD"
fi

# Define commit types and their descriptions
declare -A COMMIT_TYPES=(
    ["feat"]="Features"
    ["fix"]="Bug Fixes"
    ["docs"]="Documentation"
    ["style"]="Style Changes"
    ["refactor"]="Code Refactoring"
    ["perf"]="Performance Improvements"
    ["test"]="Tests"
    ["build"]="Build System"
    ["ci"]="CI/CD"
    ["chore"]="Chores"
)

# Generate changelog content
generate_section() {
    local type=$1
    local pattern="^${type}(\([^)]+\))?:"
    local commits=$(git log --no-merges --pretty=format:"%s|%h" ${FROM_TAG}..${TO_TAG} | grep -E "$pattern" || true)
    
    if [ ! -z "$commits" ]; then
        echo "### ${COMMIT_TYPES[$type]}"
        echo
        while IFS='|' read -r message hash; do
            # Extract scope if present
            if [[ $message =~ $type\(([^)]+)\): ]]; then
                scope="${BASH_REMATCH[1]}"
                message=${message#$type\($scope\): }
            else
                scope=""
                message=${message#$type: }
            fi
            
            # Format the commit line
            if [ ! -z "$scope" ]; then
                echo "* **${scope}:** ${message} ([${hash}](../../commit/${hash}))"
            else
                echo "* ${message} ([${hash}](../../commit/${hash}))"
            fi
        done <<< "$commits"
        echo
    fi
}

# Generate temporary changelog
TMP_CHANGELOG=$(mktemp)

{
    echo "# Changelog"
    echo
    echo "## [$(git describe --tags --abbrev=0 2>/dev/null || echo "Unreleased")] - $(date +%Y-%m-%d)"
    echo
    
    for type in "${!COMMIT_TYPES[@]}"; do
        generate_section "$type"
    done
    
    # Add breaking changes section if any
    BREAKING_CHANGES=$(git log --no-merges --pretty=format:"%B" ${FROM_TAG}..${TO_TAG} | grep -B 1 "BREAKING CHANGE:" || true)
    if [ ! -z "$BREAKING_CHANGES" ]; then
        echo "### BREAKING CHANGES"
        echo
        echo "$BREAKING_CHANGES" | sed 's/BREAKING CHANGE:/\*/g'
        echo
    fi
    
    # Add previous changelog content if it exists
    if [ -f "$CHANGELOG_FILE" ]; then
        echo "---"
        echo
        tail -n +2 "$CHANGELOG_FILE"
    fi
} > "$TMP_CHANGELOG"

# Replace the old changelog
mv "$TMP_CHANGELOG" "$CHANGELOG_FILE"

echo "Changelog generated successfully in $CHANGELOG_FILE"

