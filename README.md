# Smart-card Security SaaS (вариант 216)

**Студент:** Курбанов Умар Рашидович · **Группа:** ИД23-1 · **ВУЗ:** Финансовый университет

Контейнер безопасности для SaaS-приложения на Smart-карте: Flask, Docker (4 контейнера), Kubernetes (1 Pod / 4 контейнера), ML (Isolation Forest).

## Быстрый старт

```bash
cd smartcard-security-saas

# 1. Тестовые данные
python3 data/generate_data.py

# 2. Docker
docker compose up --build -d
docker compose ps

# 3. Проверка
chmod +x scripts/test-app.sh
./scripts/test-app.sh http://localhost:8080
```

- **Приложение:** http://localhost:8080  
- **pgAdmin:** http://localhost:5050 (`admin@example.com` / `admin123`)  
  - Add server: Host `db`, Port `5432`, User `app`, Password `smartcard_secret`, DB `smartcard_db`

## Kubernetes

```bash
docker build -t smartcard-web:1.0 ./app
chmod +x scripts/deploy-k8s.sh
./scripts/deploy-k8s.sh
kubectl port-forward -n smartcard-security pod/smartcard-security-pod 8080:80
```

## Документы для сдачи

| Файл | Назначение |
|------|------------|
| `docs/02_OTCHET.docx` | Отчёт (Word) |


## Структура

```
smartcard-security-saas/
├── app/                 # Flask + security + ML
├── nginx/
├── k8s/config.yaml
├── data/
├── docs/
├── docker-compose.yml
└── scripts/
```
