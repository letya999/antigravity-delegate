<p align="center">
  <a href="README.md">English</a> · <strong>Русский</strong>
</p>

<p align="center">
  <h1 align="center">Antigravity Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/antigravity-delegate"><img src="https://img.shields.io/badge/статус-активен-brightgreen" alt="статус"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue" alt="Лицензия: MIT"></a>
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/skills.sh-доступен-black" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-agy-purple" alt="CLI: agy">
</p>

Скилл-делегат для неинтерактивного запуска Google Antigravity (`agy`) от [Артема Летюшева](https://github.com/letya999).

Основная команда — `scripts/delegate_antigravity.py`. Главный потребитель — управляющий агент или оркестратор: каждый запуск выполняет Antigravity в ограниченном подпроцессе (`agy -p`) и возвращает структурированный JSON-конверт.

---

## Одна цель, изолированный подпроцесс, нулевое доверие

Скрипт-обёртка служит детерминированным барьером безопасности между управляющим агентом и CLI Antigravity:

- **Строго неинтерактивный запуск:** Вызывает `agy -p` напрямую через `subprocess.run(..., shell=False)` без перехвата терминала.
- **Ограничение рабочей зоны:** Автоматически передаёт `--add-dir <cwd>` для предоставления доступа только к целевому каталогу проекта.
- **Верификация результатов:** Вывод дочернего агента считается недоверенным. Управляющий агент проверяет diff и запускает тесты независимо.
- **Изоляция секретов:** Обёртка не читает, не логирует и не передаёт `GEMINI_API_KEY`, OAuth-токены, приватные ключи и файлы `.env`.

## Матрица возможностей

| Параметр / Возможность | Спецификация | Поведение и гарантии |
|---|---|---|
| **Команда запуска** | `agy -p "<task>"` | Неинтерактивный запуск в режиме print с JSON-форматированием вывода |
| **Ограничение каталога** | `--add-dir <cwd>` | Предоставляет Antigravity доступ к проекту |
| **Формат вывода** | `--output-format json` | Структурированный результат извлекается в поле `response` |
| **Синхронизация таймаута** | `--print-timeout <sec>` | Передаёт значение таймаута во внутренний watchdog Antigravity |
| **Модель безопасности** | Стандартные права | Режим по умолчанию; `--dangerously-skip-permissions` только при явном `--always-approve` |
| **Переопределение бинарника** | Переменная `AGY_BIN` | Приоритетный путь до вызова из PATH |
| **Возобновляемые сессии** | `--conversation <id>` | Опциональное продолжение существующего диалога |
| **Коды возврата** | `0, 2, 65, 124, 126, 127` | Предсказуемая маршрутизация ошибок для агентов |

## Установка

Через `npx skills`:

```bash
npx skills add letya999/antigravity-delegate
```

Или клонированием в каталог скиллов:

```bash
git clone https://github.com/letya999/antigravity-delegate.git .agents/skills/antigravity-delegate
```

## Быстрый старт

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_antigravity.py \
  --cwd "$PWD" \
  --task "Проведи аудит безопасности репозитория и выдели топ-3 риска." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_antigravity.py `
  --cwd (Get-Location).Path `
  --task "Проведи аудит безопасности репозитория и выдели топ-3 риска." `
  --timeout 45m
```

---

<details>
<summary>Схема JSON-манифеста и интеграция с агентом</summary>

Обёртка записывает `stdout.json`, `stderr.log` и `result.json` во временный каталог и выводит манифест в stdout:

```json
{
  "tool": "agy",
  "cwd": "C:\\work\\repo",
  "user_home": null,
  "environment_overrides": [],
  "exit_code": 0,
  "output_dir": "C:\\Temp\\antigravity-delegate-xyz",
  "stdout": "C:\\Temp\\antigravity-delegate-xyz\\stdout.json",
  "stderr": "C:\\Temp\\antigravity-delegate-xyz\\stderr.log",
  "response": "Извлеченный текст ответа или структурированные данные",
  "raw": {
    "status": "SUCCESS",
    "response": "..."
  }
}
```

Если Antigravity возвращает статус отличный от `SUCCESS` или пустой ответ при нулевом коде завершения, обёртка возвращает код `65`.

</details>

<details>
<summary>Флаги CLI и параметры запуска</summary>

| Флаг | Тип | Описание |
|---|---|---|
| `--cwd` | Путь (обязательный) | Рабочая папка проекта. Завершается с кодом `2`, если каталог не существует. |
| `--task` | Строка (обязательный) | Текст поручения / промпта для Antigravity. |
| `--timeout` | Время (по умолчанию: `45m`) | Таймаут в формате `90s`, `45m`, `2h` или число секунд. |
| `--always-approve` | Флаг | Передаёт `--dangerously-skip-permissions` для автономных изменений файлов. |
| `--conversation` | Строка | Идентификатор диалога для продолжения сессии. |
| `--user-home` | Путь | Изолированная пользовательская папка через `HOME` и `USERPROFILE`. |
| `--output-dir` | Путь | Каталог для сохранения логов и манифеста. |

</details>

<details>
<summary>Правила безопасности и изоляция секретов</summary>

- **Защита учётных данных:** Скрипт никогда не считывает, не печатает и не передаёт `GEMINI_API_KEY`, профили `~/.antigravity` или куки.
- **Безопасность по умолчанию:** Автоодобрение правок отключено. Обход подтверждений возможен только при явном флаге `--always-approve`.
- **Защита от рекурсии:** Делегированный агент не должен рекурсивно вызывать скиллы-делегаты.

</details>

<details>
<summary>Протокол независимой верификации</summary>

Результаты работы делегата считаются непроверенными. Если задача предполагала изменение файлов:

1. Проверьте изменения: `git diff --stat` и `git diff`.
2. Запустите тесты независимо: `pytest`, `npm test` и т.д.
3. Проверьте добавленные зависимости перед коммитом.

</details>

<details>
<summary>Набор тестов</summary>

Тесты на базе стандартной библиотеки `unittest` без сетевых вызовов и реального бинарника:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Точки входа скилла</summary>

- [SKILL.md](SKILL.md) — Инструкция скилла для кодинг-агентов.
- [QUICKSTART.md](QUICKSTART.md) — Краткое руководство.
- [references/runtime-setup.md](references/runtime-setup.md) — Кроссплатформенная проверка окружения.
- [references/headless-reference.md](references/headless-reference.md) — Справочник флагов CLI.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Индекс обнаружения для skills.sh.
- [dist/antigravity-delegate.zip](dist/antigravity-delegate.zip) — Архив скилла.

</details>

<details>
<summary>Лицензия</summary>

MIT License. См. полный текст в [LICENSE](LICENSE). Copyright (c) 2026 Artem Letyushev.

</details>
