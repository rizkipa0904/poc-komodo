#!/usr/bin/env bash
set -e

# Ganti ini dengan token Vault kamu
VAULT_TOKEN="sssssssss"

# Endpoint Vault
VAULT_URL="https://vault.sshub.web.id/v1/kv/data/staging/odoo"

echo "Fetching config from Vault..."
# Ambil data Vault
response=$(curl -s \
  --header "X-Vault-Token:${VAULT_TOKEN}" \
  --request GET \
  "${VAULT_URL}")

# Parsing JSON
# Misal data Vault structured seperti:
# {
#   "data": {
#     "data": {
#       "admin_passwd": "...",
#       "db_host": "...",
#       ...
#     }
#   }
# }
# Kita extract satu per satu
admin_passwd=$(echo "$response" | jq -r '.data.data.admin_passwd')
db_host=$(echo "$response" | jq -r '.data.data.db_host')
db_port=$(echo "$response" | jq -r '.data.data.db_port')
db_user=$(echo "$response" | jq -r '.data.data.db_user')
db_password=$(echo "$response" | jq -r '.data.data.db_password')
addons_path=$(echo "$response" | jq -r '.data.data.addons_path')
data_dir=$(echo "$response" | jq -r '.data.data.data_dir')
log_level=$(echo "$response" | jq -r '.data.data.log_level')

# Generate file odoo.conf
cat > odoo.conf <<EOF
[options]
admin_passwd = ${admin_passwd}
db_host = ${db_host}
db_port = ${db_port}
db_user = ${db_user}
db_password = ${db_password}
addons_path = ${addons_path}
data_dir = ${data_dir}
log_level = ${log_level}
EOF

echo "odoo.conf created successfully."
