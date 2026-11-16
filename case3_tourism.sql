-- Кейс-задача № 3. База данных «Туризм» (MySQL 8).
-- 4 таблицы-справочника: clients, countries, tours, services
-- 1 таблица переменной информации: orders (заказы туров)

DROP DATABASE IF EXISTS tourism;
CREATE DATABASE tourism CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tourism;

-- Справочник 1. Клиенты
CREATE TABLE clients (
    client_id   INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(150) NOT NULL,
    phone       VARCHAR(20)  NOT NULL,
    email       VARCHAR(100) UNIQUE,
    passport_no VARCHAR(20)  NOT NULL UNIQUE
) ENGINE = InnoDB;

-- Справочник 2. Страны
CREATE TABLE countries (
    country_id   INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    visa_needed  BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE = InnoDB;

-- Справочник 3. Туры (каждый тур относится к стране)
CREATE TABLE tours (
    tour_id         INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(150)  NOT NULL,
    country_id      INT           NOT NULL,
    nights          INT           NOT NULL CHECK (nights > 0),
    price_per_person DECIMAL(10,2) NOT NULL CHECK (price_per_person >= 0),
    CONSTRAINT fk_tours_country FOREIGN KEY (country_id)
        REFERENCES countries (country_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Справочник 4. Дополнительные услуги (страховка, трансфер, экскурсии…)
CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100)  NOT NULL UNIQUE,
    price      DECIMAL(10,2) NOT NULL CHECK (price >= 0)
) ENGINE = InnoDB;

-- Таблица переменной информации. Заказы:
-- ссылается на ключи справочников через внешние ключи
CREATE TABLE orders (
    order_id     INT AUTO_INCREMENT PRIMARY KEY,
    client_id    INT  NOT NULL,
    tour_id      INT  NOT NULL,
    service_id   INT  NULL,                       -- услуга необязательна
    order_date   DATE NOT NULL,
    start_date   DATE NOT NULL,
    persons      INT  NOT NULL DEFAULT 1 CHECK (persons > 0),
    status       ENUM('новый', 'оплачен', 'отменён') NOT NULL DEFAULT 'новый',
    CONSTRAINT fk_orders_client  FOREIGN KEY (client_id)  REFERENCES clients (client_id),
    CONSTRAINT fk_orders_tour    FOREIGN KEY (tour_id)    REFERENCES tours (tour_id),
    CONSTRAINT fk_orders_service FOREIGN KEY (service_id) REFERENCES services (service_id)
) ENGINE = InnoDB;

CREATE INDEX idx_orders_date ON orders (order_date);

-- Тестовые данные
INSERT INTO countries (name, visa_needed) VALUES
    ('Турция', FALSE), ('Египет', FALSE), ('Италия', TRUE), ('Таиланд', FALSE);

INSERT INTO clients (full_name, phone, email, passport_no) VALUES
    ('Иванова Мария Петровна', '+77011234567', 'ivanova@mail.ru', 'N1234567'),
    ('Петров Олег Сергеевич',  '+77017654321', 'petrov@mail.ru',  'N7654321'),
    ('Сидорова Анна Ивановна', '+77015556677', 'sidorova@mail.ru', 'N5556677');

INSERT INTO tours (title, country_id, nights, price_per_person) VALUES
    ('Анталья — пляжный отдых', 1, 7, 250000.00),
    ('Хургада — дайвинг',       2, 10, 320000.00),
    ('Рим и Флоренция',         3, 6, 480000.00),
    ('Пхукет — острова',        4, 12, 550000.00);

INSERT INTO services (name, price) VALUES
    ('Медицинская страховка', 8000.00),
    ('Трансфер из аэропорта', 12000.00),
    ('Экскурсионный пакет',   40000.00);

INSERT INTO orders (client_id, tour_id, service_id, order_date, start_date, persons, status) VALUES
    (1, 1, 1,    '2025-06-16', '2025-07-10', 2, 'оплачен'),
    (2, 3, 3,    '2025-06-20', '2025-08-01', 1, 'новый'),
    (3, 2, NULL, '2025-06-25', '2025-07-15', 3, 'оплачен');

-- Пример запроса: заказы с суммой (тур × кол-во человек + услуга)
SELECT o.order_id,
       c.full_name               AS client,
       t.title                   AS tour,
       co.name                   AS country,
       o.persons,
       s.name                    AS service,
       t.price_per_person * o.persons + COALESCE(s.price, 0) AS total,
       o.status
FROM orders o
JOIN clients   c  ON c.client_id  = o.client_id
JOIN tours     t  ON t.tour_id    = o.tour_id
JOIN countries co ON co.country_id = t.country_id
LEFT JOIN services s ON s.service_id = o.service_id
ORDER BY o.order_date;
