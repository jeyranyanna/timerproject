# чтобы изменить настройки KIVY по умолчанию мы используем этот модуль конфигурации
from kivy.config import Config
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window

Config.set('graphics', 'resizable', True) # нет фиксированного размера окна

Window.size = (375, 667)   # айфон 8
#Window.size = (414, 896)  # айфон 11
#Window.size = (360, 640)  # android small
#Window.size = (360, 800)  # android large


import time
import datetime
import threading # модуль, который позволяет программировать запуск нескольких операций одновременно
from kivy.properties import StringProperty, NumericProperty, ObjectProperty

# для воспроизведения звука
# кроссплатформенная библиотека для для воспроизведения файлов wav без каких-либо зависимостей
import simpleaudio
filename = 'finish.wav'
wave_object = simpleaudio.WaveObject.from_wave_file( filename )


class Timer(MDScreen, threading.Thread):
    # начальные данные

    is_time_for_long_pause = False               # флаг для отслеживания длительного перерыва
    running = False
    count_pomidoros = NumericProperty()          # количество помидорок
    session_before_long_pause = 0                # номер сессии до длительного перерыва
    current_running_time = NumericProperty(0)    # текущее время
    how_long_to_work = 25 * 60                   # время рабочей сессии
    how_long_to_pause = 5 * 60                   # время отдыха
    how_long_to_pause_long = 15 * 60             # время длительного перерыва
    remaining_time = NumericProperty(0)          # оставшееся время до следующей итерации
    running_time = StringProperty('')            # текущее время в строковом формате
    is_stopped = False
    bt_start_timer = ObjectProperty(None)


    # запуск таймера в потоке
    def run_thread(self):
        print(self)
        while self.running and not Timer.is_stopped:
            if self.current_running_time > 0:  # когда таймер работает
                self.current_running_time -= 1  # уменьшение таймера

                # расчет оставшегося времени в зависимости от типа сессии (работа, отдых, долгий перерыв)
                if (self.is_time_for_long_pause == True): # длительный перерыв
                    self.remaining_time = (self.how_long_to_pause_long - self.current_running_time) * 360 / self.how_long_to_pause_long
                elif self.session_before_long_pause % 2 != 0:
                    self.remaining_time = (self.how_long_to_work - self.current_running_time) * 360 / self.how_long_to_work
                else:
                    self.remaining_time = (self.how_long_to_pause - self.current_running_time) * 360 / self.how_long_to_pause


                # воспроизведение звука
                if self.current_running_time == 0:
                    wave_object.play()


            else: # когда сессия окончена или таймер запущен в первый раз
                self.session_before_long_pause += 1
                self.is_time_for_long_pause = False
                self.remaining_time = 0  # обнуление оставшегося времени
                if self.session_before_long_pause % 2 != 0: # когда работа (так как при первом запуске попадаем  сюда)
                    self.count_pomidoros += 1 # расчет количества помидорок
                    self.current_running_time = self.how_long_to_work
                    self.ids.condition.text = "Сохраняйте концентрацию"
                else:
                    self.current_running_time = self.how_long_to_pause
                    self.ids.condition.text = "Расслабьтесь"
                self.ids.count_pomidoros_text.text = f'Круг {self.count_pomidoros}/4'
                if (self.session_before_long_pause == 8):
                    self.is_time_for_long_pause = True
                    self.current_running_time = self.how_long_to_pause_long
                    self.session_before_long_pause = 0 # сброс итераций до длительного перерыва
                    self.count_pomidoros = 0 # сброс помидорок
                    self.ids.condition.text = "Длительный перерыв"
                    self.ids.count_pomidoros_text.text = ""



            self.running_time = str(datetime.timedelta(seconds=self.current_running_time))
            time.sleep(1)   # симуляция задержки выполнения программы на 1 секунду
                            # позволяет отсрочить выполнение вызываемого потока на указанное количество секунд

    # запуск таймера
    def start_timer(self):
        self.ids.bt_start_timer.disabled = True # блокировка кнопки play
        Timer.is_stopped = False
        if(Timer.is_stopped):
            self.reset_timer()
        self.running = True
        thread = threading.Thread(target=self.run_thread) # передача функции в конструктор
        thread.start()  # запуск потока при вызове внутреннего метода run

    # остановка таймера
    def pause_timer(self):
        self.ids.bt_start_timer.disabled = False
        self.running = False

    # сброс осуществляется через возврат к исходным данным таймера
    def reset_timer(self):
        self.ids.bt_start_timer.disabled = False
        self.is_time_for_long_pause = False
        self.running = False
        self.count_pomidoros = 0
        self.session_before_long_pause = 0
        self.current_running_time = 0
        self.remaining_time = 0
        self.running_time = ""
        self.ids.count_pomidoros_text.text = ""
        self.ids.condition.text = "Запустите таймер для начала фокусировки"

    # остановка таймера при выходе из приложения
    def stop_timer(self):
        self.is_time_for_long_pause = False
        self.running = False
        self.count_pomidoros = 0
        self.session_before_long_pause = 0
        self.current_running_time = 0
        self.remaining_time = 0
        self.running_time = ""
        self.running = False
        Timer.is_stopped = True
        return self.running