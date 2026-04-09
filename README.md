

## Development Guide

### Initial Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/clydewatts1/PDFA_Webservices_And_Application_Big_Project.git
```

2. Create environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   The DAO prefers `mysql-connector-python` but can fall back to `PyMySQL` if the active Python environment cannot negotiate the configured MySQL authentication plugin.

3. Configure database access before starting the Flask app:

   ```bash
   copy .env.example .env  # On PowerShell: Copy-Item .env.example .env
   ```

   `DB_AUTH_PLUGIN` can be left blank for connector auto-negotiation.
   If your MySQL 8 user uses `caching_sha2_password`, set `DB_AUTH_PLUGIN=caching_sha2_password`.

4. Start the application:

   ```bash
   python app.py
   ```

For local development, prefer environment-backed credentials rather than editing `app.py`.