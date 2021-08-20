#### План миграции базы и сервисов на новый формат данных:

Убедиться, что в запросах сервисов к БД явно указаны необходимые колонки.
Например, заменить запросы вида:
```
INSERT INTO main_table
VALUES (id_val, name_val, status_val, timestamp_val);
SELECT *
FROM main_table;
```
на:
```
INSERT INTO main_table (id, name, status, timestamp)
VALUES (id_val, name_val, status_val, timestamp_val);
SELECT id, name, status, timestamp
FROM main_table;
```
Иначе после добавления в таблицу новой колонки может возникнуть ошибка:
* при записи - количество переданных значений будет меньше количества колонок,
* при чтении записей, если доступ к значениям колонок осуществляется по отрицательным индексам.

Создать таблицу `name_table` и заполнить значениями из колонки `name` основной таблицы. Например, так:
```
CREATE TABLE name_table (
    id  INTEGER NOT NULL PRIMARY KEY,
    name    TEXT UNIQUE
);
INSERT INTO name_table (name)
SELECT DISTINCT name
FROM main_table;
```
В основную таблицу добавить колонку `tmp_id`. Например:
```
ALTER TABLE main_table
ADD tmp_id INTEGER;
ALTER TABLE main_table
ADD FOREIGN KEY (tmp_id) REFERENCES name_table(id);
```
Обновить сервисы типа __А__ чтобы в основную таблицу они добавляли записи в формате
`id, name, status, timestamp, tmp_id`
и для новых значений `name` создавали новые записи в таблице `name_table`.

Заполнить пустые значения колонки `tmp_id` соответствующими значениями `id` из таблицы `name_table`:
```
UPDATE main_table
SET tmp_id = name_table.id
FROM name_table
WHERE main_table.name = name_table.name;
```
Обновить сервисы типа __Б__ чтобы они считывали данные в новом формате используя поле `tmp_id` и таблицу `name_table`.

Обновить севисы типа __А__ чтобы они добавляли записи в формате `id, status, timestamp, tmp_id` оставляя поле `name` пустым.

Очистить значения колонки `name` в основной таблице:
```
UPDATE main_table SET name = NULL;
```
Переименовать колонку `name` основной таблицы в `name_id`:
```
ALTER TABLE main_table CHANGE COLUMN name name_id INTEGER;
ALTER TABLE main_table
ADD FOREIGN KEY (name_id) REFERENCES name_table(id);
```
Обновить севисы типа __А__ чтобы они добавляли записи в формате `id, name_id, status, timestamp, tmp_id`, где значения `name_id` и `tmp_id` одинаковы.

Заполнить пустые значения колонки `name_id` значениями из `tmp_id`:
```
UPDATE main_table SET name_id = tmp_id;
```
Обновить сервисы типа __Б__ чтобы они чтобы они считывали данные в формате `id, name_id, status, timestamp`.

Обновить сервисы типа __А__ чтобы они добавляли записи в новом формате оставляя значение `tmp_id` пустым.

Удалить колонку `tmp_id`:
```
ALTER TABLE main_table DROP COLUMN tmp_id;
```

При необходимости, убрать явное указание полей из запросов сервисов к БД, добавленное в начале миграции.