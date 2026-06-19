# JSON Table Converter

MVP веб-приложения для преобразования JSON произвольной структуры в таблицу с предпросмотром, фильтрацией, сортировкой и экспортом CSV/XLSX.

## Запуск

```bash
docker compose up --build
```

Frontend: http://localhost:5173  
Backend healthcheck: http://localhost:8000/api/health

## API

- `POST /api/analyze` — анализ структуры, candidate roots, рекомендованный root path.
- `POST /api/transform` — flatten/normalize в rows/columns, preview first 100 rows по умолчанию.
- `POST /api/export/csv` — экспорт текущих rows в UTF-8 CSV с BOM.
- `POST /api/export/xlsx` — экспорт текущих rows в XLSX.
- `POST /api/parse-file` — серверный парсинг `.json` с лимитом размера.

## Тесты backend

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. pytest
```

## Стратегия по умолчанию

Если корень — массив объектов, используется `$`. Если корень — объект, анализатор ищет наиболее табличный массив объектов и рекомендует его как root path. Если массивов нет, строится одна строка из flatten-объекта. Вложенные объекты становятся колонками dot notation. Массивы объектов в режиме `explode` дают дополнительные строки. Массивы примитивов по умолчанию объединяются в одну ячейку.
