import struct
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Список команд и их соответствующие коды 
COMMANDS = {
    "LOAD": 10,
    "LOAD_MEM": 49,
    "STORE": 0,
    "GE": 8,
}


def pretty_print_xml(elem):
    """Форматирование XML с отступами."""
    raw_xml = ET.tostring(elem, encoding="utf-8")
    parsed = minidom.parseString(raw_xml)
    return parsed.toprettyxml(indent="  ")


def assemble(input_file, binary_file, log_file):
    instructions = []
    binary_data = bytearray()

    with open(input_file, "r") as f:
        for line in f:
            # Удаление комментариев и пробелов 
            line = line.split(";")[0].strip()
            if not line:
                continue

                # Разделяем команду и аргументы
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                raise ValueError(f"Некорректная строка: '{line}'")

            command = parts[0]
            if command not in COMMANDS:
                raise ValueError(f"Неизвестная команда: {command}")

            opcode = COMMANDS[command]

            # Разбор аргументов 
            try:
                args = [int(x.replace("R", "").strip()) for x in parts[1].split(",")]
            except ValueError:
                raise ValueError(f"Ошибка парсинга аргументов в строке: '{line}'")

                # Генерация байт команды
            if command == "LOAD":
                if len(args) != 2:
                    raise ValueError(f"Некорректное число аргументов для {command}")
                b, c = args
                binary = struct.pack("<BHB", opcode, b, c)
            elif command == "LOAD_MEM":
                if len(args) != 2:
                    raise ValueError(f"Некорректное число аргументов для {command}")
                b, c = args
                binary = struct.pack("<BBB", opcode, b, c)
            elif command == "STORE":
                if len(args) != 3:
                    raise ValueError(f"Некорректное число аргументов для {command}")
                b, c, d = args
                binary = struct.pack("<BH", opcode << 8 | b, (c << 4) | d)
            elif command == "GE":
                if len(args) != 4:
                    raise ValueError(f"Некорректное число аргументов для {command}")
                b, c, d, e = args
                if e < 0 or e > 16383:
                    raise ValueError(f"Смещение E (поле E) выходит за пределы диапазона: {e}")
                binary = struct.pack("<BHBH", opcode, b, c, e)
            else:
                raise ValueError(f"Не реализовано для команды: {command}")

            binary_data.extend(binary)
            instructions.append({
                "opcode": opcode,
                "args": args,
                "bytes": " ".join(f"{b:02X}" for b in binary),
            })

            # Сохранение бинарного файла
    with open(binary_file, "wb") as bf:
        bf.write(binary_data)

        # Генерация XML-лога
    root = ET.Element("log")
    for instr in instructions:
        instr_elem = ET.SubElement(root, "instruction", opcode=str(instr["opcode"]))
        ET.SubElement(instr_elem, "args").text = str(instr["args"])
        ET.SubElement(instr_elem, "bytes").text = instr["bytes"]

    formatted_xml = pretty_print_xml(root)

    with open(log_file, "w", encoding="utf-8") as lf:
        lf.write(formatted_xml)

        # Дополнительно: вывод дампа бинарных данных для отладки
    with open("program_dump.txt", "w") as dump_file:
        dump_file.write(" ".join(f"{byte:02X}" for byte in binary_data))

    # Укажите пути к файлам для тестирования


input_file = "input.asm"
binary_file = "program.bin"
log_file = "program_log.xml"

# Запуск ассемблера 
assemble(input_file, binary_file, log_file)