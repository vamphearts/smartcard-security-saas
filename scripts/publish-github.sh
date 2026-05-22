#!/bin/bash
# Публикация репозитория на GitHub (один раз: gh auth login)
set -euo pipefail
cd "$(dirname "$0")/.."

REPO_NAME="${1:-smartcard-security-saas}"

if ! command -v gh &>/dev/null; then
  echo "Установите GitHub CLI: brew install gh"
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "Войдите в GitHub (откроется браузер):"
  gh auth login
fi

echo "Создаю репозиторий: $REPO_NAME"
gh repo create "$REPO_NAME" \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description "Зачётная работа: Smart-card Security SaaS, вариант 216 (Flask, Docker, K8s, ML)"

echo ""
echo "Готово! Ссылка для преподавателя:"
gh repo view --web 2>/dev/null || gh repo view --json url -q .url
