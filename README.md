# candy_delivery
Это тестовое задание для школы бэкенда Яндекса. Используется библиотека fastapi, основанная на starlette. 

СУБД - sqlite, базируется в delivery_app_db. 

Необходимые зависимости перечислены в requirements.txt.

Для установки зависиимостей выполнить ``` pip install -r requirements.txt ```

## Развертка 
- Активировать виртуальную среду: ``` source /home/entrant/candy_env/bin/activate ```
- Перейти в ``` /home/entrant/candy_app ```
- Запустить uvicorn на нужном хосте и порту: ``` uvicorn main:app --reload --host 0.0.0.0 --port 8080 ```

## Тесты
Используется библиотека pytest, все тесты лежат в ``` /home/entrant/candy_app/tests.py ```

Для исполнения тестов выполнить находясь в директории с tests.py ``` pytest tests.py ```

Для повторного исполнения тестов необходимо очистить полученные с предыдущих тестов данные в БД sqlite следующим набором команд:
``` 
DELETE FROM couriers;
DELETE FROM orders;
DELETE FROM assigned_orders;
DELETE FROM complete_orders; 
```
