# Trading Log Processor

## Описание задания

Цель проекта — создать промежуточный слой хранения данных для быстрого получения информации об активных заявках. Задача состоит из двух частей:

1. На основании лога заявок (Staging layer) реализовать промежуточный слой хранения данных, который позволяет быстро извлекать информацию об активных заявках.
   - **Реализация:** схема базы данных и алгоритм трансформации данных.
2. Написать SQL-запрос для получения информации из промежуточного слоя о:
   - Активной заявке с самой высокой ценой покупки.
   - Активной заявке с самой низкой ценой продажи.
   - Для заданного инструмента на определённый момент времени.

---

## Решение

В качестве промежуточного слоя выбраны:

- **API**: Реализовано с использованием `FastAPI`.
- **База данных**: PostgreSQL со следующей структурой таблицы:

```sql
id SERIAL PRIMARY KEY,                  -- Уникальный идентификатор
instrument TEXT NOT NULL,               -- Название инструмента
operation CHAR(1) NOT NULL,             -- Тип операции (покупка 'B' или продажа 'S')
price NUMERIC NOT NULL,                 -- Цена заявки
remaining_qty INTEGER NOT NULL,         -- Оставшееся количество
timestamp TIMESTAMP NOT NULL            -- Временная метка заявки
```

## Установка и запуск

### Предварительные требования

- Установите [Docker](https://www.docker.com/).
- Склонируйте репозиторий.
- Создайте файл `.env` для хранения переменных окружения:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password123
```

---

## Запуск проекта

### 1. Соберите и запустите контейнеры

```bash
docker-compose up --build
```

### 2. После успешного запуска API будет доступно по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Функциональность API

### 1. Загрузка данных в БД

Для выполнения первого задания реализован эндпоинт:

- **POST** `/api/load-csv`

**Параметры:**

- Загрузите CSV-файл с логом заявок. Пример данных доступен по ссылке: [MOEX](https://www.moex.com/ru/orders?orderlogs) (файлы типа `_fut_ord.csv`).

**Пример ответа:**

```json
{
  "detail": "Data successfully loaded into the database."
}
```

### 2. Получение информации о заявках

Для выполнения второго задания реализован эндпоинт:

- **GET** `/api/active_orders/price_info`

**Параметры:**

- `instrument`: Название инструмента (например, `SAH9`).
- `timestamp`: Временная отметка в формате `YYYY-MM-DD HH:MM:SS` (например, 2018-12-28 18:50:34.017000).

**Пример ответа:**

```json
{
  "highest_buy_price": data,
  "lowest_sell_price": data
}
```

### 3. CRUD операции

Для управления заявками реализованы стандартные CRUD операции. Эндпоинты доступны в теге `/api/orders/`.

**Полный список запросов** и их параметры можно найти в [Swagger-документации](http://localhost:8000/docs).

---

### Примечания

- Время загрузки данных из файла может достигать **25 секунд** в зависимости от размера CSV-файла.
- Для корректной обработки данных убедитесь, что ваш CSV-файл соответствует формату Московской биржи (Срочный рынок, тип-A).
