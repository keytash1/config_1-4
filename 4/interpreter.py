import struct
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Размер памяти УВМ
MEMORY_SIZE = 1024
# Инициализация памяти и регистров
memory = [0] * MEMORY_SIZE
registers = [0] * 64


def pretty_print_xml(elem):
    """Форматирование XML с отступами."""
    raw_xml = ET.tostring(elem, encoding="utf-8")
    parsed = minidom.parseString(raw_xml)
    return parsed.toprettyxml(indent="  ")


def execute_instruction(opcode, args):
    """Выполнение одной инструкции."""
    global memory, registers

    if opcode == 10:  # Загрузка константы
        a, b, c = args
        registers[b] = c
    elif opcode == 49:  # Чтение из памяти
        a, b, c = args
        addr = registers[c]
        if addr < 0 or addr >= MEMORY_SIZE:
            raise ValueError(f"Некорректный адрес памяти: {addr}")
        registers[b] = memory[addr]
    elif opcode == 0:  # Запись в память
        a, b, c, d = args
        addr = registers[c] + d
        if addr < 0 or addr >= MEMORY_SIZE:
            raise ValueError(f"Некорректный адрес памяти: {addr}")
        memory[addr] = registers[b]
    elif opcode == 8:  # Операция сравнения >=
        a, b, c, d, e = args
        addr = registers[d]
        if addr < 0 or addr >= MEMORY_SIZE:
            raise ValueError(f"Некорректный адрес памяти: {addr}")
        operand1 = registers[b]
        operand2 = memory[addr]
        result_addr = registers[c] + e
        if result_addr < 0 or result_addr >= MEMORY_SIZE:
            raise ValueError(f"Некорректный адрес памяти: {result_addr}")
        memory[result_addr] = 1 if operand1 >= operand2 else 0
    else:
        raise ValueError(f"Неизвестная команда с opcode={opcode}")


def interpret(binary_file, result_file, memory_range):
    """Интерпретатор УВМ."""
    global memory, registers

    # Чтение бинарного файла
    with open(binary_file, "rb") as bf:
        binary_data = bf.read()

        # Разбор бинарных инструкций
    i = 0
    while i < len(binary_data):
        opcode = binary_data[i] & 0x1F  # Извлекаем 5 бит для opcode

        if opcode == 10:  # Загрузка константы
            a = binary_data[i + 1] & 0x3F  # Биты 0—5 для A
            b = (binary_data[i + 1] >> 6) & 0x3F  # Биты 6—11 для B
            c = struct.unpack_from("<I", binary_data, i + 2)[0]  # Биты 12—32 для C
            execute_instruction(opcode, [a, b, c])
            i += 5  # Загрузка константы должна занимать 5 байтов

        elif opcode == 49:  # Чтение из памяти
            a = binary_data[i + 1] & 0x3F  # Биты 0—5 для A
            b = (binary_data[i + 1] >> 6) & 0x3F  # Биты 6—11 для B
            c = (binary_data[i + 2] & 0x3F)  # Биты 12—17 для C
            execute_instruction(opcode, [a, b, c])
            i += 3  # Чтение из памяти должно занимать 3 байта

        elif opcode == 0:  # Запись в память
            a = binary_data[i] & 0x3F  # Биты 0—5 для A
            b = (binary_data[i] >> 6) & 0x3F  # Биты 6—11 для B
            c = binary_data[i + 1] & 0x3F  # Биты 12—17 для C
            d = struct.unpack_from("<H", binary_data, i + 2)[0]  # Биты 18—31 для D
            execute_instruction(opcode, [a, b, c, d])
            i += 4  # Запись в память должна занимать 4 байта

        elif opcode == 8:  # Операция сравнения >=
            a = binary_data[i] & 0x3F  # Биты 0—5 для A
            b = (binary_data[i] >> 6) & 0x3F  # Биты 6—11 для B
            c = binary_data[i + 1] & 0x3F  # Биты 12—17 для C
            d = binary_data[i + 2] & 0x3F  # Биты 18—23 для D
            e = struct.unpack_from("<H", binary_data, i + 3)[0]  # Биты 24—37 для E
            execute_instruction(opcode, [a, b, c, d, e])
            i += 5  # Операция сравнения >= должна занимать 5 байтов

        else:
            raise ValueError(f"Неизвестная команда с opcode={opcode}")

            # Сохранение диапазона памяти в XML
    start, end = memory_range
    if start < 0 or end >= MEMORY_SIZE or start > end:
        raise ValueError(f"Некорректный диапазон памяти: {memory_range}")
    root = ET.Element("memory")
    for addr in range(start, end + 1):
        mem_elem = ET.SubElement(root, "cell", address=str(addr))
        mem_elem.text = str(memory[addr])

    formatted_xml = pretty_print_xml(root)
    with open(result_file, "w", encoding="utf-8") as rf:
        rf.write(formatted_xml)

        # Укажите пути к файлам для тестирования


binary_file = "program.bin"  # Путь к бинарному файлу
result_file = "result.xml"  # Путь к файлу для сохранения результата
memory_range = (0, 15)  # Диапазон памяти для вывода (например, с 0 по 15)

# Запуск интерпретатора
interpret(binary_file, result_file, memory_range)