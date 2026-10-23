# Security & Secrets Management

**CRITICAL DIRECTIVES FOR ALL AGENTS:**

1. **NEVER COMMIT SECRETS**: You are strictly forbidden from committing or pushing any of the following to the git repository:
   - Private keys, PEM files, or certificates
   - API keys, personal access tokens, or unencrypted passwords
   - Configuration or `.env` files that contain raw credentials

2. **USE GITHUB SECRETS**: For automated CI/CD pipelines (like GitHub Actions), retrieve any required credentials exclusively via GitHub Secrets (`${{ secrets.* }}`).

3. **VERIFY GITIGNORE**: Always ensure that `.gitignore` is properly configured to exclude temporary downloads (`*.htm`), local caches, and sensitive files before staging changes.
