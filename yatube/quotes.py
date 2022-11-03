def test_invert(invertaser):
    """Тест алогритма инвертирования строки."""
    print(f'{test_invert.__doc__}')
    print(f'Тестирование алгоритма {invertaser.__name__}')

    source = 'Попугай'
    inversed = 'йагупоП'

    assert invertaser(source) == inversed, (
        f'Алгоритм в {invertaser.__name__} работает неправильно '
        f'со строкой "{source}"'
    )

    source = ''
    inversed = ''

    assert invertaser(source) == inversed, (
        f'Алгоритм {invertaser.__name__} работает неправильно с пустой строкой'
    )

    print(f'Тест для {invertaser.__name__} пройден успешно')


# Ниже - несколько функций, инвертирующих строку.
# Их и будем тестировать.
def recursion_invertor(text):
    """Инвертирует строчку рекурсивно."""
    if len(text) == 0:
        return text
    return recursion_invertor(text[1:]) + text[0]


def slice_invertor(text):
    """Инвертирует строчку срезом."""
    return text[::-1]


def iterator_invertor(text):
    """Инвертирует строчку обратной итерацией."""
    return ''.join(reversed(text))


def reverselist_invertor(text):
    """Инвертирует строчку переворотом списка."""
    inversed_list = list(text)
    inversed_list.reverse()
    return ''.join(inversed_list)


def unworked_sort(text):
    """Функция не делает ничего."""


# Вызов тестирующей функции для каждой функции-инвертора
test_invert(recursion_invertor)
test_invert(slice_invertor)
test_invert(iterator_invertor)
test_invert(reverselist_invertor)
test_invert(unworked_sort)
