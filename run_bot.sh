#!/bin/bash

# Перейти в директорию проекта
cd /Users/mikhailmakurov/mjob/

# Создать виртуальное окружение, если оно не существует
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Активировать виртуальное окружение
source venv/bin/activate

# Обновить pip
python -m pip install --upgrade pip

# Установить или обновить зависимости
pip install -r requirements.txt --upgrade

# Установить psutil, если еще не установлен
pip install psutil

# Запустить бота
python3 main.py