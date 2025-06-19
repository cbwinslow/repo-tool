#!/bin/bash

# Enhanced security scanning script for RepoTool
# This script performs comprehensive security analysis

set -e  # Exit on error

# Configuration
REPORT_DIR="reports/security"
CURRENT_DATE=$(date +%Y%m%d)
REPORT_FILE="${REPORT_DIR}/security_report_${CURRENT_DATE}.md"
CRITICAL_ISSUES_FOUND=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
    CRITICAL_ISSUES_FOUND=1
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Initialize report
init_report() {
    mkdir -p "${REPORT_DIR}"
    cat > "${REPORT_FILE}" <<EOL
# Security Scan Report
Generated: $(date)

## Summary

EOL
}

# Run Bandit for Python security checks
run_bandit() {
    log "Running Bandit security checks..."
    
    bandit -r src/ -f json -o "${REPORT_DIR}/bandit.json" || true
    
    # Parse results
    BANDIT_ISSUES=$(jq '.results | length' "${REPORT_DIR}/bandit.json")
    if [ "${BANDIT_ISSUES}" -gt 0 ]; then
        error "Found ${BANDIT_ISSUES} security issues with Bandit"
        echo "### Bandit Security Issues" >> "${REPORT_FILE}"
        echo "Found ${BANDIT_ISSUES} potential security issues:" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
        jq -r '.results[] | "- [" + .issue_severity + "] " + .issue_text + " in " + .filename + ":" + (.line_number|tostring)' "${REPORT_DIR}/bandit.json" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
    else
        log "No issues found with Bandit"
        echo "### Bandit Security Check: ✅ Passed" >> "${REPORT_FILE}"
    fi
}

# Run Safety check for Python dependencies
run_safety() {
    log "Checking Python dependencies for known vulnerabilities..."
    
    safety check --json > "${REPORT_DIR}/safety.json" || true
    
    # Parse results
    SAFETY_ISSUES=$(jq '. | length' "${REPORT_DIR}/safety.json")
    if [ "${SAFETY_ISSUES}" -gt 0 ]; then
        error "Found ${SAFETY_ISSUES} vulnerable dependencies"
        echo "### Vulnerable Dependencies" >> "${REPORT_FILE}"
        echo "Found ${SAFETY_ISSUES} vulnerable dependencies:" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
        jq -r '.[] | "- " + .[0] + " " + .[1] + " [" + .[4] + "]"' "${REPORT_DIR}/safety.json" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
    else
        log "No vulnerable dependencies found"
        echo "### Dependency Security Check: ✅ Passed" >> "${REPORT_FILE}"
    fi
}

# Run npm audit
run_npm_audit() {
    log "Checking npm dependencies for vulnerabilities..."
    
    npm audit --json > "${REPORT_DIR}/npm_audit.json" || true
    
    # Parse results
    NPM_ISSUES=$(jq '.metadata.vulnerabilities.total' "${REPORT_DIR}/npm_audit.json")
    if [ "${NPM_ISSUES}" -gt 0 ]; then
        error "Found ${NPM_ISSUES} npm vulnerabilities"
        echo "### npm Vulnerabilities" >> "${REPORT_FILE}"
        echo "Found ${NPM_ISSUES} vulnerabilities:" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
        jq -r '.advisories | to_entries[] | .value | "- " + .title + " [" + .severity + "]"' "${REPORT_DIR}/npm_audit.json" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
    else
        log "No npm vulnerabilities found"
        echo "### npm Security Check: ✅ Passed" >> "${REPORT_FILE}"
    fi
}

# Run Trivy for container scanning
run_trivy() {
    log "Scanning container image for vulnerabilities..."
    
    if ! command -v trivy &> /dev/null; then
        warn "Trivy not installed - skipping container scan"
        return
    fi
    
    trivy image --format json --output "${REPORT_DIR}/trivy.json" "ghcr.io/cbwinslow/repo-tool:latest" || true
    
    # Parse results
    TRIVY_ISSUES=$(jq '.Results[].Vulnerabilities | length' "${REPORT_DIR}/trivy.json" | awk '{sum += $1} END {print sum}')
    if [ "${TRIVY_ISSUES}" -gt 0 ]; then
        error "Found ${TRIVY_ISSUES} container vulnerabilities"
        echo "### Container Vulnerabilities" >> "${REPORT_FILE}"
        echo "Found ${TRIVY_ISSUES} vulnerabilities:" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
        jq -r '.Results[].Vulnerabilities[] | select(.Severity == "CRITICAL" or .Severity == "HIGH") | "- [" + .Severity + "] " + .VulnerabilityID + ": " + .Title' "${REPORT_DIR}/trivy.json" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
    else
        log "No container vulnerabilities found"
        echo "### Container Security Check: ✅ Passed" >> "${REPORT_FILE}"
    fi
}

# Run secret scanning
run_secret_scan() {
    log "Scanning for secrets in codebase..."
    
    if ! command -v gitleaks &> /dev/null; then
        warn "Gitleaks not installed - skipping secret scan"
        return
    fi
    
    gitleaks detect --no-git --report-format json --report-path "${REPORT_DIR}/gitleaks.json" || true
    
    # Parse results
    GITLEAKS_ISSUES=$(jq '. | length' "${REPORT_DIR}/gitleaks.json")
    if [ "${GITLEAKS_ISSUES}" -gt 0 ]; then
        error "Found ${GITLEAKS_ISSUES} potential secrets"
        echo "### Secret Detection" >> "${REPORT_FILE}"
        echo "Found ${GITLEAKS_ISSUES} potential secrets:" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
        jq -r '.[] | "- " + .Description + " in " + .File' "${REPORT_DIR}/gitleaks.json" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
    else
        log "No secrets found"
        echo "### Secret Detection: ✅ Passed" >> "${REPORT_FILE}"
    fi
}

# Run SAST analysis
run_sast() {
    log "Running static analysis..."
    
    if ! command -v semgrep &> /dev/null; then
        warn "Semgrep not installed - skipping SAST"
        return
    fi
    
    semgrep scan --config auto --json --output "${REPORT_DIR}/semgrep.json" || true
    
    # Parse results
    SEMGREP_ISSUES=$(jq '.results | length' "${REPORT_DIR}/semgrep.json")
    if [ "${SEMGREP_ISSUES}" -gt 0 ]; then
        error "Found ${SEMGREP_ISSUES} code security issues"
        echo "### Static Analysis" >> "${REPORT_FILE}"
        echo "Found ${SEMGREP_ISSUES} issues:" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
        jq -r '.results[] | "- [" + .extra.severity + "] " + .extra.message + " in " + .path + ":" + (.start.line|tostring)' "${REPORT_DIR}/semgrep.json" >> "${REPORT_FILE}"
        echo '```' >> "${REPORT_FILE}"
    else
        log "No SAST issues found"
        echo "### Static Analysis: ✅ Passed" >> "${REPORT_FILE}"
    fi
}

# Check for outdated dependencies
check_outdated_deps() {
    log "Checking for outdated dependencies..."
    
    echo "### Outdated Dependencies" >> "${REPORT_FILE}"
    echo "#### Python Packages" >> "${REPORT_FILE}"
    pip list --outdated --format=json | jq -r '.[] | "- " + .name + " (Current: " + .version + ", Latest: " + .latest_version + ")"' >> "${REPORT_FILE}"
    
    echo "#### npm Packages" >> "${REPORT_FILE}"
    npm outdated --json | jq -r 'to_entries[] | "- " + .key + " (Current: " + .value.current + ", Latest: " + .value.latest + ")"' >> "${REPORT_FILE}"
}

# Generate final report summary
generate_summary() {
    log "Generating report summary..."
    
    # Count issues by severity
    CRITICAL=$(grep -c '\[CRITICAL\]' "${REPORT_FILE}" || echo 0)
    HIGH=$(grep -c '\[HIGH\]' "${REPORT_FILE}" || echo 0)
    MEDIUM=$(grep -c '\[MEDIUM\]' "${REPORT_FILE}" || echo 0)
    LOW=$(grep -c '\[LOW\]' "${REPORT_FILE}" || echo 0)
    
    # Insert summary at the top
    TMP_FILE=$(mktemp)
    cat > "${TMP_FILE}" <<EOL
# Security Scan Report
Generated: $(date)

## Summary
- Critical Issues: ${CRITICAL}
- High Issues: ${HIGH}
- Medium Issues: ${MEDIUM}
- Low Issues: ${LOW}

Overall Status: $([ ${CRITICAL_ISSUES_FOUND} -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")

EOL
    
    tail -n +4 "${REPORT_FILE}" >> "${TMP_FILE}"
    mv "${TMP_FILE}" "${REPORT_FILE}"
}

# Main execution
main() {
    log "Starting security scan..."
    
    init_report
    run_bandit
    run_safety
    run_npm_audit
    run_trivy
    run_secret_scan
    run_sast
    check_outdated_deps
    generate_summary
    
    log "Security scan complete. Report saved to ${REPORT_FILE}"
    
    if [ ${CRITICAL_ISSUES_FOUND} -eq 1 ]; then
        error "Critical security issues found. Please review the report."
        exit 1
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

