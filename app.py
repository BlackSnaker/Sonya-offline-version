import sounddevice as sd
import vosk
from fuzzywuzzy import fuzz
import random
import json
import queue
from subprocess import call
import webbrowser
import torch
import time
import os

def bot_speak(text):
    print("Бот говорит: " + text)

VA_CMD_LIST = {
    "help": ('список команд', 'команды', 'что ты умеешь', 'твои навыки', 'навыки','расскажи о себе'),
    "joke": ('расскажи анекдот', 'рассмеши', 'шутка', 'расскажи шутку', 'пошути', 'развесели'),
    "browser": ('браузер', 'запусти браузер'),
    "volume up": ('сделай громче','увеличь громкость'),
    "volume down": ('сделай тише','уменши громкость','тише','сделай потише','потише'),
    "volume full": ('верни звук','включи звук'),
    "volume mute": ('выключи звук','отключи звук'),
    "reboot": ('перезагрузи','перезагрузка'),
    "shutdown": ('выключи компьютер','отключи компьютер')
    
}

q = queue.Queue()

model = vosk.Model("model_small_ru")

device = sd.default.device[0]  # Assuming you want the first device
samplerate = int(sd.query_devices(device, "input")["default_samplerate"])

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def main():
    try:
        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=16000,
            device=device,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            rec = vosk.KaldiRecognizer(model, samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    data = json.loads(rec.Result())["text"]
                    recognize(data)
                    filter_cmd(data)
    except Exception as e:
        print("An error occurred:", str(e))

def recognize(data):
    print("Пользователь сказал: " + data)
    if data.startswith("соня"):
        cmd = recognize_cmd(filter_cmd(data))
        if cmd['cmd'] not in VA_CMD_LIST.keys():
            bot_speak("Что?")
        else:
            execute_cmd(cmd['cmd'])

def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in VA_CMD_LIST.items():
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt
    return rc

def execute_cmd(cmd: str):
    if cmd == 'help':
        help_command()
    elif cmd == 'joke':
        joke_command()
    elif cmd == 'browser':
        browser_command()
    elif cmd == 'volume up':
        volume_up_command()
    elif cmd == 'volume down':
        volume_down_command()
    elif cmd == 'volume mute':
        volume_mute_command()
    elif cmd == 'volume full':
        volume_full_command()
    elif cmd == 'reboot':
        reboot_command()
    elif cmd == 'shutdown':
        shutdown_command()

def help_command():
    text = "Я умею: ..."
    text += "рассказывать анекдоты ..."
    text += "управлять громкостью"
    text += "выключать и перезагружать компьютер,"
    text += "и открывать браузер"
    bot_speak(text)

def joke_command():
    jokes = ['Как смеются программисты? ... ехе ехе ехе',
             'ЭсКьюЭль запрос заходит в бар, подходит к двум столам и спрашивает .. «м+ожно присоединиться?»',
             'Программист это машина для преобразования кофе в код']
    bot_speak(random.choice(jokes))

def browser_command():
    webbrowser.open("google.com")
    bot_speak("открываю")

def volume_up_command():
    call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
    bot_speak("громкость увеличена на десять процентов")

def volume_down_command():
    call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
    bot_speak("громкость уменьшена на десять процентов")

def volume_mute_command():
    call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
    bot_speak("громкость отключена")

def volume_full_command():
    call(["amixer", "-D", "pulse", "sset", "Master", "100%"])
    bot_speak("громкость включена")

def reboot_command():
    call(["reboot"])

def shutdown_command():
    call(["shutdown", "-f", "now"])

def filter_cmd(data):
    cmd = data
    cmd = cmd.replace('соня', '').strip()
    cmd = cmd.replace('  ', ' ').strip()
    return cmd

if __name__ == "__main__":
    main()
