
dev:
	docker-compose up --build

test:
	docker build -t airflow-test --target test .
	docker run -t airflow-test test