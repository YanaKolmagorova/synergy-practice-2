"""
Кейс-задача № 4. Веб-приложение «Турагентство» (архитектура WEB-приложения).

Браузер (клиент)  <-- HTTP -->  веб-сервер + приложение (Python/Flask)  <-- SQL -->  база данных (SQLite)

Что умеет:
  /         — каталог туров (данные из БД)
  /order    — форма оформления заказа (запись в БД)
  /orders   — список заказов с итоговой суммой (JOIN нескольких таблиц)

Запуск:  pip install flask   ->   python app.py   ->   открыть http://127.0.0.1:5000
"""
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, g, redirect, render_template_string, request, url_for

DB_PATH = Path(__file__).with_name("tourism.db")
app = Flask(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL, phone TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS countries (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS tours (
    tour_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    country_id INTEGER NOT NULL REFERENCES countries(country_id),
    nights INTEGER NOT NULL CHECK (nights > 0),
    price_per_person REAL NOT NULL CHECK (price_per_person >= 0));
CREATE TABLE IF NOT EXISTS services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, price REAL NOT NULL);
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL REFERENCES clients(client_id),
    tour_id INTEGER NOT NULL REFERENCES tours(tour_id),
    service_id INTEGER REFERENCES services(service_id),
    order_date TEXT NOT NULL,
    persons INTEGER NOT NULL CHECK (persons > 0));
"""

SEED = """
INSERT INTO countries (name) VALUES ('Турция'), ('Египет'), ('Италия'), ('Таиланд');
INSERT INTO tours (title, country_id, nights, price_per_person) VALUES
  ('Анталья — пляжный отдых', 1, 7, 250000), ('Хургада — дайвинг', 2, 10, 320000),
  ('Рим и Флоренция', 3, 6, 480000), ('Пхукет — острова', 4, 12, 550000);
INSERT INTO services (name, price) VALUES
  ('Медицинская страховка', 8000), ('Трансфер из аэропорта', 12000), ('Экскурсионный пакет', 40000);
"""


def get_db():
    """Одно подключение к БД на один запрос пользователя."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Создаёт таблицы и тестовые данные при первом запуске."""
    first_run = not DB_PATH.exists()
    with sqlite3.connect(DB_PATH) as db:
        db.executescript(SCHEMA)
        if first_run:
            db.executescript(SEED)


LAYOUT = """<!doctype html><html lang="ru"><head><meta charset="utf-8">
<title>Турагентство</title>
<style>
 body{font-family:sans-serif;max-width:900px;margin:30px auto;padding:0 16px;color:#222}
 nav a{margin-right:16px} table{border-collapse:collapse;width:100%}
 td,th{border:1px solid #ccc;padding:6px 10px;text-align:left} th{background:#eef}
 label{display:block;margin-top:10px} .err{color:#b00}
</style></head><body>
<nav><a href="{{ url_for('tours') }}">Каталог туров</a>
<a href="{{ url_for('new_order') }}">Оформить заказ</a>
<a href="{{ url_for('orders') }}">Заказы</a></nav><hr>
{% block content %}{% endblock %}</body></html>"""


def page(body, **ctx):
    return render_template_string(LAYOUT.replace("{% block content %}{% endblock %}", body), **ctx)


@app.route("/")
def tours():
    rows = get_db().execute(
        "SELECT t.title, c.name AS country, t.nights, t.price_per_person "
        "FROM tours t JOIN countries c ON c.country_id = t.country_id ORDER BY t.price_per_person"
    ).fetchall()
    return page("""<h1>Каталог туров</h1><table>
      <tr><th>Тур</th><th>Страна</th><th>Ночей</th><th>Цена за человека</th></tr>
      {% for r in rows %}<tr><td>{{r.title}}</td><td>{{r.country}}</td>
      <td>{{r.nights}}</td><td>{{ '%.0f'|format(r.price_per_person) }}</td></tr>{% endfor %}
      </table>""", rows=rows)


@app.route("/order", methods=["GET", "POST"])
def new_order():
    db = get_db()
    error = None
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        tour_id = request.form.get("tour_id", type=int)
        service_id = request.form.get("service_id", type=int)  # пусто -> None
        persons = request.form.get("persons", type=int)
        # Проверка ввода на сервере (не доверяем браузеру)
        if not name or not phone:
            error = "Заполните ФИО и телефон."
        elif not persons or not 1 <= persons <= 20:
            error = "Количество человек — от 1 до 20."
        elif not tour_id or not db.execute("SELECT 1 FROM tours WHERE tour_id=?", (tour_id,)).fetchone():
            error = "Выберите тур из списка."
        else:
            # Параметры передаются через «?» — это защищает от SQL-инъекций
            cur = db.execute("INSERT INTO clients (full_name, phone) VALUES (?, ?)", (name, phone))
            db.execute(
                "INSERT INTO orders (client_id, tour_id, service_id, order_date, persons) VALUES (?, ?, ?, ?, ?)",
                (cur.lastrowid, tour_id, service_id, date.today().isoformat(), persons),
            )
            db.commit()
            return redirect(url_for("orders"))
    tours_list = db.execute("SELECT tour_id, title FROM tours").fetchall()
    services = db.execute("SELECT service_id, name, price FROM services").fetchall()
    return page("""<h1>Оформить заказ</h1>
      {% if error %}<p class="err">{{error}}</p>{% endif %}
      <form method="post">
        <label>ФИО <input name="full_name" required></label>
        <label>Телефон <input name="phone" required></label>
        <label>Тур <select name="tour_id">{% for t in tours %}
          <option value="{{t.tour_id}}">{{t.title}}</option>{% endfor %}</select></label>
        <label>Доп. услуга <select name="service_id"><option value="">— нет —</option>
          {% for s in services %}<option value="{{s.service_id}}">{{s.name}} ({{'%.0f'|format(s.price)}})</option>
          {% endfor %}</select></label>
        <label>Человек <input name="persons" type="number" min="1" max="20" value="1"></label>
        <p><button>Оформить</button></p>
      </form>""", tours=tours_list, services=services, error=error)


@app.route("/orders")
def orders():
    rows = get_db().execute(
        "SELECT o.order_id, o.order_date, c.full_name, t.title, o.persons, s.name AS service, "
        "       t.price_per_person * o.persons + COALESCE(s.price, 0) AS total "
        "FROM orders o JOIN clients c ON c.client_id = o.client_id "
        "JOIN tours t ON t.tour_id = o.tour_id "
        "LEFT JOIN services s ON s.service_id = o.service_id ORDER BY o.order_id DESC"
    ).fetchall()
    return page("""<h1>Заказы</h1>{% if not rows %}<p>Заказов пока нет.</p>{% else %}<table>
      <tr><th>№</th><th>Дата</th><th>Клиент</th><th>Тур</th><th>Чел.</th><th>Услуга</th><th>Сумма</th></tr>
      {% for r in rows %}<tr><td>{{r.order_id}}</td><td>{{r.order_date}}</td><td>{{r.full_name}}</td>
      <td>{{r.title}}</td><td>{{r.persons}}</td><td>{{r.service or '—'}}</td>
      <td>{{'%.0f'|format(r.total)}}</td></tr>{% endfor %}</table>{% endif %}""", rows=rows)


init_db()

if __name__ == "__main__":
    app.run(debug=False)
