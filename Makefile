.PHONY: data up down test k8s logs

data:
	python3 data/generate_data.py

up:
	docker compose up --build -d

down:
	docker compose down

test:
	chmod +x scripts/test-app.sh
	./scripts/test-app.sh http://localhost:8080

k8s:
	chmod +x scripts/deploy-k8s.sh
	./scripts/deploy-k8s.sh

logs:
	docker compose logs -f
