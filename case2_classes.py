"""
Кейс-задача № 2.
Тестовая программа, которая демонстрирует работу методов базового
и производного классов.

Базовый класс  — Tour (тур).
Производный    — AllInclusiveTour (тур «всё включено»): наследует всё от Tour,
                 добавляет своё поле и переопределяет два метода.
Язык: Python 3.
"""
import unittest


class Tour:
    """Базовый класс: обычный тур."""

    def __init__(self, country, nights, price_per_night):
        self.country = country
        self.nights = nights
        self.price_per_night = price_per_night

    def total_price(self):
        """Полная стоимость тура."""
        return self.nights * self.price_per_night

    def description(self):
        """Короткое описание тура."""
        return f"Тур в {self.country}, ночей: {self.nights}, цена: {self.total_price()} руб."


class AllInclusiveTour(Tour):          # в скобках — от кого наследуемся
    """Производный класс: тур «всё включено» с доплатой за питание."""

    def __init__(self, country, nights, price_per_night, food_per_day):
        super().__init__(country, nights, price_per_night)  # вызываем конструктор родителя
        self.food_per_day = food_per_day                     # новое поле, которого нет у Tour

    def total_price(self):             # переопределение: считаем по-своему
        base = super().total_price()   # берём расчёт родителя...
        return base + self.nights * self.food_per_day  # ...и добавляем питание

    def description(self):             # переопределение описания
        return super().description() + " (всё включено)"


def demo():
    """Демонстрация: одинаковые вызовы — разное поведение (полиморфизм)."""
    tours = [
        Tour("Турцию", 7, 5000),
        AllInclusiveTour("Египет", 7, 5000, 2000),
    ]
    for t in tours:
        print(type(t).__name__, "->", t.description())
    # метод, который производный класс НЕ переопределял, всё равно доступен:
    print("Страна второго тура (поле из базового класса):", tours[1].country)


class TestTours(unittest.TestCase):
    def test_base_price(self):
        self.assertEqual(Tour("Турцию", 7, 5000).total_price(), 35000)

    def test_derived_price(self):
        self.assertEqual(AllInclusiveTour("Египет", 7, 5000, 2000).total_price(), 49000)

    def test_derived_is_also_base(self):
        self.assertIsInstance(AllInclusiveTour("Египет", 1, 1, 1), Tour)

    def test_description_overridden(self):
        self.assertTrue(AllInclusiveTour("Египет", 1, 1, 1).description().endswith("(всё включено)"))


if __name__ == "__main__":
    demo()
    print()
    unittest.main(verbosity=2)
