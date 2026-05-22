# ОТЧЁТ ПО ЗАЧЁТНОЙ РАБОТЕ

**Тема:** Разработка контейнера для обеспечения безопасности приложения на Smart-карте при угрозе получения несанкционированного доступа (вариант 216)

**Студент:** Курбанов Умар Рашидович, группа ИД23-1  
**Университет:** Финансовый университет  
**Руководитель:** _________________________

---

## 1. Техническое задание

Разработано ТЗ (файл `docs/01_TZ.md`). Определены цели, функции контейнера безопасности, алгоритм ML-анализа, состав из 4 контейнеров, критерии приёмки.

## 2. Разработка приложения (SaaS, Flask)

Реализовано веб-приложение на **Flask** с модулями:

- `security/auth.py` — Security Container (блокировка, пороги);
- `security/audit.py` — журнал в PostgreSQL;
- `security/anomaly.py` — Isolation Forest, графики matplotlib.

Точка входа: `app/app.py`. UI: `templates/index.html`.

**API:**

- `GET /health` — проверка сервиса;
- `POST /api/access` — проверка доступа к Smart-карте;
- `POST /api/analyze` — пакетный ML-анализ CSV;
- `GET /api/logs` — журнал аудита.

## 3. Четыре контейнера и доступ к nginx

| Контейнер | Роль | Порт |
|-----------|------|------|
| smartcard-nginx | Reverse proxy, rate limit | 8080→80 |
| smartcard-web | Flask/Gunicorn | внутренний 8000 |
| smartcard-db | PostgreSQL | 5432 |
| smartcard-pgadmin | Админ БД | 5050→80 |

Файл `docker-compose.yml`, конфигурация nginx `nginx/nginx.conf` (проксирование на `web:8000`, limit_req).

## 4. Интеллектуальная обработка данных

**Алгоритм:** Isolation Forest (scikit-learn), признаки: failed PIN, RPM, hour.

**Табличное представление:** топ-20 сессий с `anomaly_score`, `ml_decision`.

**Визуальное:** гистограмма scores, scatter PIN/RPM, pie Normal/Anomaly (base64 PNG в JSON).

При наличии метки `label` вычисляется точность относительно класса `attack`.

## 5. Docker — развёртывание 4 контейнеров

```bash
cd smartcard-security-saas
docker compose up --build -d
docker compose ps
```

Сеть `smartcard-net` (bridge), DNS-имена сервисов: `web`, `db`, `nginx`, `pgadmin`.

## 6. Взаимодействие контейнеров и сеть

- Пользователь → nginx:80 → web:8000;
- web → db:5432 (DATABASE_URL);
- pgadmin → db:5432 (настройка в UI pgAdmin: host `db`, user `app`).

Healthcheck для `web` и `db`. Зависимости `depends_on` с condition `service_healthy`.

## 7. Манифест Kubernetes config.yaml

Файл `k8s/config.yaml` содержит:

- Namespace `smartcard-security`;
- ConfigMap `app-config`, `nginx-config`;
- Secret `app-secrets`;
- **Pod** `smartcard-security-pod` с 4 контейнерами в одном поде;
- Service NodePort (80→30080, pgadmin→30050).

В Pod контейнеры используют `127.0.0.1` для связи web↔db↔nginx.

## 8. Развёртывание кластера Kubernetes

```bash
docker build -t smartcard-web:1.0 ./app
# minikube: minikube image load smartcard-web:1.0
kubectl apply -f k8s/config.yaml
kubectl get pods -n smartcard-security
kubectl port-forward -n smartcard-security pod/smartcard-security-pod 8080:80
```

Скрипт автоматизации: `scripts/deploy-k8s.sh`.

## 9. Генерация тестовых данных

```bash
python3 data/generate_data.py -o testdata.csv
```

Состав согласован с ТЗ: 500 записей, метки `normal` / `attack`. Поля соответствуют п.6 ТЗ.

## 10. Проверка работоспособности

**Автотест:**

```bash
chmod +x scripts/test-app.sh
./scripts/test-app.sh http://localhost:8080
```

**Ручная проверка:**

1. Открыть http://localhost:8080
2. Загрузить `data/testdata.csv` → «Анализ CSV»
3. Убедиться в сводке ML, таблице и 3 графиках
4. Проверить блокировку при failed_pin ≥ 3
5. pgAdmin: http://localhost:5050 (admin@example.com / admin123)

**Ожидаемые результаты ML:** обнаружено ~15% аномалий (contamination=0.15), accuracy vs labels > 0.85 на синтетике.

## Выводы

Разработан полный стек защиты SaaS-приложения Smart-карты: контейнер безопасности с блокировкой, аудит, ML-аналитика, развёртывание в Docker и Kubernetes. Угроза несанкционированного доступа нейтрализуется комбинацией политик и детекции аномалий.

## Приложения

- `docs/01_TZ.md` — ТЗ  
- `docs/03_PREZENTACIYA.md` — текст слайдов  
- `docker-compose.yml`, `k8s/config.yaml`  
- `data/testdata.csv`

---

*Дата: май 2025 · Курбанов У.Р.*
