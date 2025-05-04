# CN Agent

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**CN Agent** — это программная система для моделирования реалистичной пользовательской активности в социальной сети Mastodon с использованием LLM-агентов. Проект реализует граф логики на основе фреймворка LangGraph, интегрируется с OpenAI API для генерации контента и использует SQLite для хранения памяти агента. Логирование осуществляется через langsmith для отслеживания действий агента в реальном времени.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
  - [Locally](#locally)
  - [Using Docker](#using-docker)
- [Usage](#usage)
- [Example Scenario](#example-scenario)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Graph-based Logic**: Управление поведением агента с помощью графа логики, реализованного в LangGraph.
- **Mastodon Integration**: Взаимодействие с Mastodon API для публикации постов, комментирования, лайков и подписок.
- **LLM-powered Content Generation**: Генерация текстов (постов, комментариев) с использованием OpenAI API, настроенная под профиль пользователя.
- **Context Analysis**: Обработка входящих данных (постов, упоминаний, трендов) и адаптация их для принятия решений агентом.
- **Memory Management**: Хранение истории активности агента в SQLite для предотвращения повторных действий.
- **Real-time Logging**: Отслеживание действий агента через langsmith.
- **Docker Support**: Контейнеризация приложения для упрощения развертывания.

## Architecture

Проект реализует граф логики, состоящий из узлов и ребер, которые моделируют поведение агента. Основные узлы:

1. **Initialization**: Загрузка профиля пользователя (интересы, стиль общения).
2. **Context Analysis**: Обработка внешних данных (посты, комментарии, упоминания).
3. **Decision Making**: Выбор действия (пост, лайк, ответ, подписка) на основе правил.
4. **Action Execution**: Выполнение действия с генерацией контента через OpenAI API.
5. **Termination**: Завершение цикла при достижении лимита активности.

Ребра графа включают обязательные (последовательные) и опциональные (условные) переходы, реализованные в LangGraph. Подробности см. в разделе 2.2.3 документации проекта.

## Project Structure

```plaintext
CN_agent/
├── /src
│   ├── /graph           # Логика графа (LangGraph)
│   ├── /mastodon        # Модули для работы с Mastodon API
│   ├── /models          # Структуры данных (профиль пользователя, контекст)
├── /config
│   ├── config.yaml      # Конфигурация (Mastodon API, OpenAI API, LLM)
├── /data
│   ├── memory.sqlite    # SQLite база для хранения памяти агента
├── Dockerfile           # Шаблон для контейнеризации
├── main.py              # Точка входа приложения
├── requirements.txt     # Зависимости проекта
├── README.md            # Документация
```

## Prerequisites

- **Python**: 3.11
- **Docker**: (опционально, для контейнеризации)
- **Mastodon Account**: Токен доступа для Mastodon API
- **OpenAI API Key**: Для генерации контента
- **langsmith Account**: (опционально, для логирования)

## Installation

1. Клонируйте репозиторий:

```bash
git clone https://github.com/kykazabra/CN_agent.git
cd CN_agent
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. (Опционально) Подготовьте Docker для контейнеризации (см. [Using Docker](#using-docker)).

## Configuration

1. Скопируйте пример конфигурации:

```bash
cp config/config_example.yaml config/config.yaml
```

2. Отредактируйте `config/config.yaml`, указав:

- **Mastodon API**:
  - `access_token`: Токен доступа к Mastodon API.
  - `api_base_url`: URL сервера Mastodon (например, `https://mastodon.social`).
- **OpenAI API**:
  - `api_key`: Ключ API OpenAI.
  - `model`: Модель LLM (например, `gpt-4`).
  - `temperature`: Температура генерации (например, `0.7`).
  - `top_p`: Параметр top-p (например, `0.9`).
- **langsmith**:
  - (Опционально) Настройки для логирования.

Пример `config.yaml`:

```yaml
mastodon:
  access_token: "your_mastodon_access_token"
  api_base_url: "https://mastodon.social"
openai:
  api_key: "your_openai_api_key"
  model: "gpt-4"
  temperature: 0.7
  top_p: 0.9
langsmith:
  enabled: false
  api_key: "your_langsmith_api_key"
```

> **Note**: Храните токены и ключи в безопасном месте. Используйте переменные окружения для чувствительных данных в продакшене.

## Running the Application

### Locally

1. Убедитесь, что `config.yaml` настроен.
2. Запустите приложение:

```bash
python main.py
```

Агент начнет обрабатывать потоковые данные от Mastodon и выполнять действия согласно графу логики.

### Using Docker

1. Соберите Docker-образ:

```bash
docker build -t cn_agent .
```

2. Запустите контейнер, указав том для персистентного хранения SQLite и переменные окружения:

```bash
docker run --name cn_agent \
  -v $(pwd)/data:/app/data \
  -e MASTODON_ACCESS_TOKEN=your_mastodon_token \
  -e OPENAI_API_KEY=your_openai_key \
  cn_agent
```

> **Tip**: Используйте Docker Compose для управления несколькими агентами или сложными конфигурациями.

## Usage

После запуска агент будет:

1. Загружать профиль пользователя из `config.yaml`.
2. Анализировать входящие данные (посты, упоминания) через `mastodon.StreamListener`.
3. Принимать решения о действиях (пост, лайк, ответ, подписка) с использованием LLM.
4. Выполнять действия через Mastodon API, генерируя контент через OpenAI API.
5. Сохранять историю активности в `data/memory.sqlite`.
6. Логировать действия через langsmith (если включено).

Логи можно отслеживать в консоли или через интерфейс langsmith.

## Example Scenario

1. **Инициализация**: Загружается профиль `{interests: ["tech"], style: "informal"}`.
2. **Анализ контекста**: Обнаружено упоминание `@tcar Привет, как дела?`.
3. **Принятие решения**: Выбрано действие "ответить".
4. **Выполнение**: Сгенерирован ответ: `Привет, все хорошо! А как твои?`. Ответ публикуется.
5. **Обновление памяти**: Действие сохраняется в SQLite.
6. **Завершение**: Цикл завершается, если лимит активности достигнут.
