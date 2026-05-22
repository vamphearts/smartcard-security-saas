# Публикация на GitHub

Локальный репозиторий уже создан и закоммичен.

## Быстрый способ (рекомендуется)

В терминале:

```bash
cd ~/Desktop/Dev/smartcard-security-saas
chmod +x scripts/publish-github.sh
./scripts/publish-github.sh
```

При первом запуске выберите в `gh auth login`:
- GitHub.com
- HTTPS
- Login with a web browser

После этого репозиторий появится на GitHub и ссылку можно отправить преподавателю.

## Вручную (если скрипт не сработал)

1. https://github.com/new → имя `smartcard-security-saas` → **Public** → Create (без README)

2. В терминале:

```bash
cd ~/Desktop/Dev/smartcard-security-saas
git remote add origin https://github.com/ВАШ_ЛОГИН/smartcard-security-saas.git
git push -u origin main
```

Замените `ВАШ_ЛОГИН` на свой ник GitHub.

## Ссылка для преподавателя

`https://github.com/ВАШ_ЛОГИН/smartcard-security-saas`

В README есть инструкция запуска через Docker.
