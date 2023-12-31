# Объявите функцию с именем get_sq, которая вычисляет площадь прямоугольника
# по двум параметрам: width и height - ширина и высота прямоугольника.
# возвращает результат (сама ничего на экран не выводит). То есть, функция имеет сигнатуру:
#
# def get_sq(width, height): ...
#
# Определите декоратор func_show для этой функции, который отображает результат на
# экране в виде строки (без кавычек):
#
# "Площадь прямоугольника: <значение>"
#
# Вызывать функцию и декоратор не нужно, только объявить. Применять
# декоратор к функции также не нужно.
#
# Sample Input:
#
# 8 11
# Sample Output:
#
# Площадь прямоугольника: 88

# ===================== ваш код =====================
def func_show(f):
    def inner(*args):
        res = f(*args)
        print(f"Площадь прямоугольника: {res}")
        return res
    return inner
def get_sq(width, height):
    return width * height






# ===================== проверка =====================
assert func_show, "декоратор не найден"
assert get_sq(8, 11) == 88, 'недекорированная get_sq вернула не тот результат'
get_sq = func_show(get_sq)
assert get_sq(8, 11) == 88, 'декорированная get_sq вернула не тот результат'
