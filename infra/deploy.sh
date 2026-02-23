#!/usr/bin/env bash
# deploy.sh — Build and deploy MeetingBot to Azure Container Apps
#
# Usage:
#   ./infra/deploy.sh [--tag <git-sha>]
#
# Prerequisites:
#   az login (or use a service principal via AZURE_CLIENT_ID / AZURE_CLIENT_SECRET)
#   Required env vars:
#     ACR_NAME            — Azure Container Registry name (without .azurecr.io)
#     RESOURCE_GROUP      — Resource group containing the Container App
#     CONTAINER_APP_NAME  — Container App resource name
#     CONTAINER_APP_ENV   — Container App Environment name
# ---------------------------------------------------------------------------
set -euo pipefail

# ── Resolve script location ────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── Defaults ───────────────────────────────────────────────────────────────────
TAG="${1:-}"
if [[ -z "$TAG" ]]; then
  TAG="sha-$(git -C "${PROJECT_ROOT}" rev-parse --short HEAD 2>/dev/null || echo "local")"
fi

: "${ACR_NAME:?ACR_NAME env var must be set}"
: "${RESOURCE_GROUP:?RESOURCE_GROUP env var must be set}"
: "${CONTAINER_APP_NAME:=${CONTAINER_APP_NAME:-meetingbot}}"
: "${CONTAINER_APP_ENV:=${CONTAINER_APP_ENV:-meetingbot-env}}"

IMAGE="${ACR_NAME}.azurecr.io/meetingbot:${TAG}"

echo "═══════════════════════════════════════════════════"
echo "  MeetingBot Deployment"
echo "  Image   : ${IMAGE}"
echo "  RG      : ${RESOURCE_GROUP}"
echo "  App     : ${CONTAINER_APP_NAME}"
echo "═══════════════════════════════════════════════════"

# ── 1. Build + push via ACR Tasks (no local Docker daemon required) ───────────
echo ""
echo "▶  Building image with ACR Tasks…"
az acr build \
  --registry "${ACR_NAME}" \
  --image "meetingbot:${TAG}" \
  --file "${PROJECT_ROOT}/Dockerfile" \
  "${PROJECT_ROOT}"

# ── 2. Update Container App with the new image ────────────────────────────────
echo ""
echo "▶  Deploying new revision to Container Apps…"
az containerapp update \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --image "${IMAGE}"

# ── 3. Show new revision URL ──────────────────────────────────────────────────
FQDN=$(az containerapp show \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv)

echo ""
echo "✔  Deployed:  https://${FQDN}"
echo "   Image:     ${IMAGE}"
