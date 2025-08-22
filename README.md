# 🤖 Savolia AI Advanced Monitoring Bot 2025

Расширенный мониторинг бот для Savolia AI с интеграцией Render.com логов и AI аналитикой.

## 🚀 Возможности

### 📊 Основные функции
- **Real-time мониторинг** всех сервисов Render.com  
- **AI аналитика** логов и метрик
- **Интерактивные графики** и визуализация
- **Уведомления об ошибках** в реальном времени
- **Прогнозирование доходов** с ML
- **Многоязычная поддержка** (Русский/Узбекский)

### 🔥 Render.com интеграция
- Просмотр логов всех 4 сервисов: savolia-web, savolia-frontend, savolia-bot, savolia-backend
- Мониторинг статуса деплоя
- Автоматические алерты при ошибках
- Фильтрация по типам логов (ERROR, WARNING, INFO)
- Real-time стриминг критических ошибок

### 📈 Аналитика
- Системные метрики и производительность
- Анализ ошибок и аномалий  
- AI-powered инсайты
- Предсказание трендов
- Revenue аналитика

## ⚙️ Установка и настройка

### 1. Клонирование и установка зависимостей

```bash
cd /Users/jasur/Desktop/Savolia-Telegram-Monitor-Bot
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте файл с примером и заполните ваши данные:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# Обязательные параметры
BOT_TOKEN=8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk
ADMIN_PASSWORD=SavoliaAdmin2025!
RENDER_BACKEND_URL=https://savolia-backend.onrender.com

# Для просмотра Render логов (получите на https://dashboard.render.com/account/settings)
RENDER_API_KEY=rnd_xxxxxxxxxxxxxxxxxxxxxxxxxx

# Для AI анализа (опционально)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Получение Render API ключа

1. Зайдите на [dashboard.render.com](https://dashboard.render.com/account/settings)
2. Перейдите в **Account Settings**
3. Найдите **API Keys** 
4. Нажмите **Generate New API Key**
5. Скопируйте ключ в `.env` файл

### 4. Запуск бота

```bash
python advanced_bot.py
```

## 📱 Команды бота

### 🔐 Авторизация
```
/start - Запуск бота
/auth PASSWORD - Авторизация (пароль: SavoliaAdmin2025!)
/help - Список всех команд
```

### 📊 Мониторинг
```
/dashboard - Главная панель мониторинга
/status - Статус всех систем
/metrics - Системные метрики
/charts - Генерация графиков
```

### 🖥️ Render логи (НОВОЕ!)
```
/render_services - Список всех сервисов
/render_logs - Выбор сервиса для просмотра логов
/render_errors - Только ошибки по сервисам
/render_deploy - Статус деплойментов
/render_status - Общий статус системы
/render_realtime - Real-time мониторинг ошибок
/render_analyze - AI анализ логов
```

### 🧠 AI Аналитика
```
/ai_analysis - AI анализ системы
/predict - Прогнозы доходов
/analytics - Подробная аналитика
```

### 👨‍💼 Админ команды
```
/admin - Админ панель
/broadcast MESSAGE - Рассылка сообщения
/backup - Создание бэкапа данных
```

## 🔧 Функции по сервисам

Бот автоматически определяет все ваши Render сервисы и предоставляет для каждого:

### 📋 Для каждого сервиса отдельно:
- `savolia-web logs` - Логи веб-приложения
- `savolia-frontend logs` - Логи фронтенда  
- `savolia-backend logs` - Логи бэкенда
- `savolia-bot logs` - Логи Telegram бота

### 🚨 Автоматические уведомления:
- Ошибки при деплое
- Критические ошибки в логах
- Проблемы с подключением
- Server errors (500, 503)
- Timeout ошибки

## 📊 Интерфейс (на узбекском)

Бот использует узбекскую латиницу для удобства:

- `✅ Muvaffaqiyatli` - Успешно
- `❌ Xatolik` - Ошибка  
- `🔄 Yangilash` - Обновить
- `📊 Tahlil` - Анализ
- `🖥️ Render Services` - Сервисы Render
- `📋 Loglar` - Логи
- `🚨 Xatolar` - Ошибки

## 🛠️ Устранение неполадок

### Проблема: "Render API key sozlanmagan"
**Решение:** Убедитесь что в `.env` файле указан `RENDER_API_KEY`

### Проблема: "Services topilmadi"  
**Решение:** Проверьте что API ключ правильный и у вас есть сервисы в Render

### Проблема: Бот не отвечает
**Решение:** 
1. Проверьте `BOT_TOKEN`
2. Пройдите авторизацию: `/auth SavoliaAdmin2025!`

## 📁 Структура проекта

```
Savolia-Telegram-Monitor-Bot/
├── advanced_bot.py           # Главный файл бота
├── render_logs_viewer.py     # Интеграция с Render API
├── telegram-logger-bot.py    # Упрощенная версия
├── requirements.txt          # Зависимости Python
├── .env.example             # Пример конфигурации
└── README.md               # Эта инструкция
```

## 🔄 Обновления

Бот автоматически:
- Проверяет статус деплоя каждые 2 минуты
- Мониторит ошибки каждые 30 секунд  
- Генерирует AI инсайты каждый час
- Очищает старые данные ежедневно

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи бота в консоли
2. Убедитесь что все API ключи корректны
3. Перезапустите бот
4. Обратитесь к разработчику

---

**🔥 Создано специально для Savolia AI - 2025**

*Bot token: 8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk*