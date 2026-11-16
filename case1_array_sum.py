"""
Кейс-задача № 1.
Дан одномерный массив A размерности N. Найти сумму отрицательных элементов,
расположенных между максимальным и минимальным элементами.

Язык: Python 3.
"""
import random


def sum_negative_between_max_and_min(a):
    """Возвращает сумму отрицательных элементов, стоящих строго между
    максимальным и минимальным элементами массива a.
    Если максимум или минимум встречается несколько раз, берётся первое вхождение."""
    if len(a) < 3:
        return 0  # между двумя соседними элементами ничего нет

    i_max = a.index(max(a))  # индекс (номер места) максимального элемента
    i_min = a.index(min(a))  # индекс минимального элемента

    # максимум может стоять и левее, и правее минимума, поэтому упорядочиваем границы
    left, right = sorted((i_max, i_min))

    total = 0
    for x in a[left + 1:right]:  # элементы строго между границами
        if x < 0:
            total += x
    return total


def read_array():
    """Ввод массива: вручную через пробел или случайно."""
    text = input("Введите элементы массива через пробел "
                 "(или нажмите Enter для случайного массива): ").strip()
    if text:
        return [int(x) for x in text.split()]
    n = int(input("Введите размерность N: "))
    return [random.randint(-20, 20) for _ in range(n)]


def run_tests():
    """Проверка на заранее посчитанных примерах."""
    assert sum_negative_between_max_and_min([5, -1, -2, 3, -10]) == -3   # max слева, min справа
    assert sum_negative_between_max_and_min([-10, -1, 4, -2, 9]) == -3   # min слева, max справа
    assert sum_negative_between_max_and_min([1, 2, 3]) == 0              # нет отрицательных между
    assert sum_negative_between_max_and_min([9, -5]) == 0                # меньше 3 элементов
    assert sum_negative_between_max_and_min([7, 7, 7]) == 0              # все элементы равны
    print("Все тесты пройдены.")


if __name__ == "__main__":
    run_tests()
    try:
        a = read_array()
    except ValueError:
        print("Ошибка: нужно вводить только целые числа.")
    else:
        if not a:
            print("Массив пуст.")
        else:
            print("Массив:", a)
            print("Максимум:", max(a), "на позиции", a.index(max(a)))
            print("Минимум:", min(a), "на позиции", a.index(min(a)))
            print("Сумма отрицательных между ними:", sum_negative_between_max_and_min(a))
