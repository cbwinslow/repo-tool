# RepoTool Troubleshooting Guide

## Common Issues and Solutions

### Authentication Issues

#### GitHub Token Issues
```
Error: GitHub API authentication failed
```

**Possible Causes:**
1. Invalid or expired token
2. Insufficient token permissions
3. Rate limiting

**Solutions:**
1. Verify token in GitHub settings
2. Check required scopes:
   ```
   repo
   read:org
   workflow (optional)
   ```
3. Generate new token:
   ```bash
   repo-tool config --reset-token github
   ```

#### GitLab Token Issues
```
Error: GitLab API returned 401 Unauthorized
```

**Solutions:**
1. Check token expiration
2. Verify API URL configuration
3. Reset token:
   ```bash
   repo-tool config --reset-token gitlab
   ```

#### SSH Key Problems
```
Error: Permission denied (publickey)
```

**Solutions:**
1. Check SSH agent:
   ```bash
   eval $(ssh-agent -s)
   ssh-add ~/.ssh/id_ed25519
   ```
2. Verify key in service settings
3. Test connection:
   ```bash
   ssh -T git@github.com
   ```

### Download Issues

#### Network Problems
```
Error: Failed to download repository: Connection timed out
```

**Solutions:**
1. Check network connection
2. Verify proxy settings:
   ```yaml
   # ~/.config/repo_tool/config.yaml
   network:
     proxy:
       http: http://proxy:8080
       https: https://proxy:8080
   ```
3. Increase timeout:
   ```yaml
   download:
     timeout_seconds: 600
   ```

#### Disk Space Issues
```
Error: No space left on device
```

**Solutions:**
1. Clear cache:
   ```bash
   repo-tool clean cache
   ```
2. Change download location:
   ```bash
   repo-tool config --set paths.default_download ~/new_location
   ```
3. Clean old repositories:
   ```bash
   repo-tool clean repositories --older-than 30d
   ```

### Configuration Issues

#### Invalid Configuration
```
Error: Invalid configuration at paths.default_download
```

**Solutions:**
1. Reset configuration:
   ```bash
   repo-tool config --reset
   ```
2. Validate configuration:
   ```bash
   repo-tool config --validate
   ```
3. Edit manually:
   ```bash
   repo-tool config --edit
   ```

#### Permission Issues
```
Error: Permission denied: /home/user/.config/repo_tool
```

**Solutions:**
1. Check file ownership:
   ```bash
   sudo chown -R $USER:$USER ~/.config/repo_tool
   ```
2. Fix permissions:
   ```bash
   chmod 600 ~/.config/repo_tool/config.yaml
   ```

### TUI Issues

#### Display Problems
```
Error: Terminal does not support required features
```

**Solutions:**
1. Check terminal capabilities:
   ```bash
   repo-tool check-terminal
   ```
2. Set TERM variable:
   ```bash
   export TERM=xterm-256color
   ```
3. Use fallback mode:
   ```bash
   repo-tool --no-rich-display
   ```

#### Unicode Issues
```
Error: UnicodeEncodeError
```

**Solutions:**
1. Set locale:
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```
2. Use ASCII mode:
   ```bash
   repo-tool --ascii
   ```

### Message Center Issues

#### Database Errors
```
Error: SQLite database is locked
```

**Solutions:**
1. Reset database:
   ```bash
   repo-tool messages --reset
   ```
2. Repair database:
   ```bash
   repo-tool messages --repair
   ```
3. Backup and restore:
   ```bash
   repo-tool messages --backup
   repo-tool messages --restore backup.db
   ```

#### Performance Issues
```
Warning: Message center is slow to respond
```

**Solutions:**
1. Clear old messages:
   ```bash
   repo-tool messages --clear-older-than 30d
   ```
2. Optimize database:
   ```bash
   repo-tool messages --optimize
   ```
3. Adjust retention:
   ```yaml
   messages:
     retention_days: 7
     max_entries: 1000
   ```

## Diagnostic Tools

### System Check
```bash
# Run system diagnostics
repo-tool diagnostics

# Check specific component
repo-tool diagnostics auth
repo-tool diagnostics network
repo-tool diagnostics storage
```

### Log Analysis
```bash
# View recent errors
repo-tool logs --level error

# Export logs
repo-tool logs --export errors.log

# Analyze patterns
repo-tool logs --analyze
```

### Configuration Validation
```bash
# Validate all settings
repo-tool config --validate

# Test specific service
repo-tool config --test-service github

# Show effective configuration
repo-tool config --show-effective
```

### Network Diagnostics
```bash
# Test service connectivity
repo-tool test-connection github
repo-tool test-connection gitlab

# Check API rate limits
repo-tool check-limits

# Measure download speed
repo-tool speed-test
```

## Performance Optimization

### Download Performance
1. Use SSH instead of HTTPS:
   ```yaml
   services:
     github:
       prefer_ssh: true
   ```

2. Adjust concurrent downloads:
   ```yaml
   download:
     max_concurrent: 5
     chunk_size: 8192
   ```

3. Enable compression:
   ```yaml
   download:
     compression: true
     compression_level: 6
   ```

### Memory Usage
1. Limit cache size:
   ```yaml
   cache:
     max_size_mb: 1000
     cleanup_threshold: 0.8
   ```

2. Reduce message retention:
   ```yaml
   messages:
     max_entries: 1000
     cleanup_threshold: 0.9
   ```

### UI Responsiveness
1. Disable animations:
   ```yaml
   display:
     animations: false
   ```

2. Reduce update frequency:
   ```yaml
   display:
     refresh_rate: 1.0
   ```

## Recovery Procedures

### Database Recovery
1. Backup current data:
   ```bash
   repo-tool backup
   ```

2. Reset to clean state:
   ```bash
   repo-tool reset --keep-config
   ```

3. Restore from backup:
   ```bash
   repo-tool restore backup_20250619.zip
   ```

### Configuration Recovery
1. Export current config:
   ```bash
   repo-tool config --export config_backup.yaml
   ```

2. Reset to defaults:
   ```bash
   repo-tool config --reset
   ```

3. Import saved config:
   ```bash
   repo-tool config --import config_backup.yaml
   ```

### Token Recovery
1. Check token status:
   ```bash
   repo-tool auth --status
   ```

2. Reset specific token:
   ```bash
   repo-tool auth --reset github
   ```

3. Import from environment:
   ```bash
   repo-tool auth --import-env
   ```

## Reporting Issues

### What to Include
1. System information:
   ```bash
   repo-tool info --full
   ```

2. Relevant logs:
   ```bash
   repo-tool logs --export --last-hour
   ```

3. Configuration (sanitized):
   ```bash
   repo-tool config --export --sanitize
   ```

### Debug Mode
```bash
# Enable debug logging
repo-tool --debug

# Full trace mode
repo-tool --trace

# Save debug log
repo-tool --debug --log-file debug.log
```

### Support Channels
1. GitHub Issues
2. Documentation Wiki
3. Community Forums
4. Email Support

