import os
import signal
import psutil

def find_bot_process():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'python' in proc.info['name'].lower() and 'main.py' in ' '.join(proc.info['cmdline']):
            return proc.info['pid']
    return None

if __name__ == "__main__":
    bot_pid = find_bot_process()
    if bot_pid:
        print(f"Отправка сигнала SIGUSR1 процессу бота (PID: {bot_pid})")
        os.kill(bot_pid, signal.SIGUSR1)
        print("Сигнал отправлен. Бот должен перезапуститься.")
    else:
        print("Процесс бота не найден. Убедитесь, что бот запущен.")