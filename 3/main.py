import xml.etree.ElementTree as ET
import sys


def xml_to_config(node, indent=0):
    """
    Рекурсивно преобразует XML-узел в текст на учебном конфигурационном языке.
    """
    result = []
    prefix = " " * indent

    # Обработка комментариев
    if node.tag == "Comment":
        comment = node.text.strip() if node.text else ""
        result.append(f"{prefix}|#\n{prefix}{comment}\n{prefix}#|")
        return "\n".join(result)

    # Если у узла есть текстовое значение, это строка или число
    if len(node) == 0:
        value = node.text.strip() if node.text else ""
        try:
            # Если текст - это число, не добавляем кавычки
            float(value)
            result.append(value)
        except ValueError:
            # Иначе оборачиваем в кавычки
            result.append(f'"{value}"')
        return "".join(result)

    # Если у узла есть дочерние элементы, проверяем их однородность
    child_tags = [child.tag for child in node if child.tag != "Comment"]
    is_array = len(set(child_tags)) == 1

    if is_array:
        # Обрабатываем массив
        result.append("<< ")
        result.append(", ".join(xml_to_config(child) for child in node if child.tag != "Comment"))
        result.append(" >>")
    else:
        # Обрабатываем словарь
        result.append("{\n")
        for child in node:
            if child.tag == "Comment":
                # Добавляем комментарий
                result.append(xml_to_config(child, indent + 2))
            else:
                result.append(f"{prefix}  {child.tag} = {xml_to_config(child, indent + 2)}\n")
        result.append(f"{prefix}}}")

    return "".join(result)


def main(input_path, output_path):
    # Парсим XML из файла
    tree = ET.parse(input_path)
    root = tree.getroot()

    # Генерируем конфигурацию
    config = f"|#\nОсновная конфигурация приложения\n#|\nconst {root.tag} = {xml_to_config(root, 2)}"

    # Записываем результат в файл
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(config)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python script.py <input_xml_path> <output_config_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
