#!/bin/bash
# Configuration
REMOTE_DB_IP="10.0.10.243"
PROJECT_ID="minecraft-server-july-12"
ENV_FILE="/var/www/appmodules/explicolivais/.env.gcp"

echo "📡 Signaling remote database on ${REMOTE_DB_IP}..."
ssh -i "/home/ec2-user/.ssh/ec2_internal" -o BatchMode=yes -o ConnectTimeout=5 "ec2-user@${REMOTE_DB_IP}" "sudo systemctl restart mcwebapp-db.service"

echo "🔐 Fetching GCP Secrets..."
SECRET_JSON=$(gcloud secrets versions access latest --secret="PASS_CONFIG" --project="${PROJECT_ID}" --quiet)

if [ $? -eq 0 ] && [ -n "$SECRET_JSON" ]; then
    # Convert JSON to KEY=VALUE format for systemd EnvironmentFile
    python3 -c "import json, sys; data = json.loads(sys.stdin.read()); [print(f'{k}={v}') for k, v in data.items()]" <<< "$SECRET_JSON" > "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo "✅ Environment file created at ${ENV_FILE}"
else
    echo "❌ Failed to fetch secrets from GCP"
    exit 1
fi
