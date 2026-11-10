#!/bin/bash
# Move to the script's directory
cd "$(dirname "$0")"

# 1. Configuration
# DEPLOY_TOPOLOGY: "single" (default, everything on one host) or "multi" (separate DB machine)
DEPLOY_TOPOLOGY="${DEPLOY_TOPOLOGY:-single}"
PROJECT_ID="${GCP_PROJECT_ID:-minecraft-server-july-12}"
VENV_PATH=$(realpath ../app-env)

# If multi-machine topology is explicitly chosen, configure remote DB details:
REMOTE_DB_IP="${REMOTE_DB_IP:-10.0.10.243}"
SSH_KEY="${REMOTE_DB_SSH_KEY:-$HOME/.ssh/id_rsa}"
REMOTE_DB_USER="${REMOTE_DB_USER:-$USER}"

# 2. Signaling remote database (only if multi-machine topology)
if [[ "${DEPLOY_TOPOLOGY}" == "multi" ]]; then
    echo "📡 Signaling remote database on ${REMOTE_DB_IP}..."
    ssh -i "${SSH_KEY}" -o BatchMode=yes -o ConnectTimeout=5 "${REMOTE_DB_USER}@${REMOTE_DB_IP}" "sudo systemctl restart mcwebapp-db.service"
else
    echo "📦 Topology set to 'single'. Running with local / Cloud SQL database."
fi

# 3. Fetch configuration from GCP Secret Manager
SECRET_JSON=$(gcloud secrets versions access latest --secret="PASS_CONFIG" --project="${PROJECT_ID}" --quiet)

if [ $? -eq 0 ] && [ -n "$SECRET_JSON" ]; then
    # Export all keys from the JSON as environment variables
    while IFS='=' read -r key value; do
        export "$key"="$value"
    done < <(python3 -c "import json, sys; data = json.loads(sys.stdin.read()); [print(f'{k}={v}') for k, v in data.items()]" <<< "$SECRET_JSON")
else
    echo "CRITICAL: Failed to fetch secrets from GCP."
    exit 1
fi

# 4. Wait for MariaDB to be ready
if [[ "${DEPLOY_TOPOLOGY}" == "multi" ]]; then
    TARGET_DB_HOST="${REMOTE_DB_IP}"
else
    TARGET_DB_HOST="${MYSQL_HOST:-127.0.0.1}"
fi
TARGET_DB_PORT="${MYSQL_PORT:-3307}"

echo "⏳ Waiting for MariaDB on ${TARGET_DB_HOST}:${TARGET_DB_PORT} to be ready..."
for i in {1..30}; do
    # Use pymysql to do a real connection check.
    # If we get Access Denied (1045), the server is alive and ready, so we count it as a success!
    if $VENV_PATH/bin/python -c "
import pymysql, sys, os
try:
    pymysql.connect(
        host='${TARGET_DB_HOST}',
        port=int('${TARGET_DB_PORT}'),
        user=os.getenv('MYSQL_USER', 'dummy'),
        password=os.getenv('MYSQL_PASSWORD', 'dummy')
    )
except pymysql.err.OperationalError as e:
    if e.args[0] == 1045: sys.exit(0)
    sys.exit(1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
         break
    fi
    sleep 1
done

# 5. Start the application in production mode
export APP_ENV=production
export FLASK_ENV=production
export FLASK_DEBUG=0

exec $VENV_PATH/bin/python server.py
