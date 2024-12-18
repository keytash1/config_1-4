import argparse
import subprocess


def get_commit_dependencies(repo_path, date_limit):
    """Получает зависимости коммитов в репозитории до определенной даты."""
    subprocess.run(['git', 'checkout', 'master'], cwd=repo_path)  # Используем 'master' или ветку по вашему выбору

    # Получаем все коммиты до заданной даты с родителями
    commit_history = subprocess.check_output(
        ['git', 'log', '--before', date_limit, '--all', '--pretty=format:%H %P'],  # --all для всех веток
        cwd=repo_path
    ).decode('utf-8').strip().split('\n')

    commit_dependencies = {}

    # Разбираем историю коммитов
    for line in commit_history:
        parts = line.split()
        commit_hash = parts[0]
        parent_hashes = parts[1:]  # Список родителей (может быть пустым для первого коммита)
        commit_dependencies[commit_hash] = parent_hashes

    return commit_dependencies


def generate_plantuml_code(commits):
    """Генерирует код PlantUML для графа зависимостей."""
    uml = ["@startuml", "digraph G {"]
    for commit, parents in commits.items():
        for parent in parents:
            uml.append(f'    "{parent}" -> "{commit}"')
    uml.append("}")
    uml.append("@enduml")
    return "\n".join(uml)


def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей для git-репозитория")
    parser.add_argument("--repo_path", required=True, help="Путь к анализируемому репозиторию")
    parser.add_argument("--output_file", required=True, help="Путь к файлу-результату в формате PlantUML")
    parser.add_argument("--date_limit", required=True, help="Дата коммитов в формате ГГГГ-ММ-ДД")

    args = parser.parse_args()

    # Получаем зависимости коммитов
    commit_dependencies = get_commit_dependencies(args.repo_path, args.date_limit)

    # Генерируем код для визуализации в PlantUML
    uml_code = generate_plantuml_code(commit_dependencies)

    # Записываем код в файл
    with open(args.output_file, 'w') as f:
        f.write(uml_code)

    # Выводим код в консоль
    print("Сгенерированный код PlantUML:")
    print(uml_code)


if __name__ == '__main__':
    main()
