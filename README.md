# Тестовое задание: Система управления мероприятиями (Event Manager)

Описание задания представлено в task.pdf

## Запуск

0. Создать .env
```
cp .env_example .env
```

1. Поднятие контейнеров
```bash 
make up
```

2. Миграция бд
```bash 
make migrate
```

3. Запуск тестов
```bash 
make test
```
