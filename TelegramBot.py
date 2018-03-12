#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Bot Telegram para proporcionar estadisticas del servidor RPi
"""

import telebot
import psutil
import atexit
import threading
from time import sleep

BOT_TIMEOUT = 45 #Timeout para contactar con servidores de Telegram
BOT_INTERVAL = 1.5 #Intervalo de obtención de actualizaciones desde servidores de Telegram (Long Polling)

with open("TOKEN.txt", "r") as file:
    BOT_TOKEN = file.read().strip() #Leer token del archivo TOKEN.txt, eliminando saltos de línea

#Ejecutamos el polling en un bucle while True porque en caso de problemas (p.ej. timeout) se reinicia automáticamente
#De lo contrario al encontrarse con el error el script terminaría
#Se ejecuta en un thread para facilitar el cierre manual de la ejecución
def bot_polling():
    bot = None
    
    @atexit.register
    def atexit_f():
        #Esta función se ejecutará justo antes de que se cierre el script
        bot.stop_polling()
        print("Polling finalizado correctamente")
    
    print("Iniciando polling...")
    while True:
        try:
            print("Nueva instancia de bot inicializada")
            bot = telebot.TeleBot(BOT_TOKEN) #Generar nueva instancia bot
            botactions(bot)
            print("Polling funcionando!")
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
        except Exception as ex: #Error en polling
            print("Problema en polling, reiniciando en {} seg. Error:\n{}".format(BOT_TIMEOUT, ex))
            bot.stop_polling()
            sleep(BOT_TIMEOUT)
        else: #Salida limpia
            break


def botactions(bot):
    #Los Handlers se registran en cada nueva instancia de bot

    @bot.message_handler(commands=["start"])
    def comm_start(message):
        #El comando /start da la bienvenida al bot
        bot.send_message(
            message.chat.id,
            "¡Hola! Este bot envía información sobre el sistema de la RPi, como uso de CPU, memoria y disco. Consulta /help para ver los comandos disponibles."
        )
        print("Solicitado comando /start")

    @bot.message_handler(commands=["help"])
    def comm_help(message):
        #El comando /help proporciona información de ayuida sobre cómo se usa el bot
        bot.send_message(
            message.chat.id,
            "*Comandos disponibles*\n/cpu - Información del procesador\n/memoria - Información de la RAM\n/disco - Información de almacenamiento",
            parse_mode="Markdown"
        )
        print("Solicitado comando /help")

    @bot.message_handler(commands=["cpu", "procesador", "micro"])
    def comm_cpu(message):
        #Los comandos /cpu, /procesador y /micro proporcionan el uso de CPU actual de la RPi
        print("Solicitado comando /cpu")
        bot.send_chat_action(message.chat.id, "typing") #Mostrar estado "Escribiendo" por parte del bot
        cpu = psutil.cpu_percent(interval=1, percpu=True) #Devuelve listado de porcentaje uso de cpu por núcleos (p.ej. [2.0, 0.0, 100.0, 2.0])
        texto = "*Uso de CPU:* {}%\n".format(sum(cpu)/len(cpu))
        
        for i in range(len(cpu)):
            texto += "\n*CPU{}:* {}%".format(i, cpu[i])
        
        bot.reply_to(message, texto, parse_mode="Markdown")


    @bot.message_handler(commands=["memoria", "mem", "memory"])
    def comm_memory(message):
        #Los comandos /memoria, /mem y /memory proporcionan datos sobre memoria RAM y SWAP de la RPi
        print("Solicitado comando /memoria")
        bot.send_chat_action(message.chat.id, "typing") #Mostrar estado "Escribiendo" por parte del bot
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        #Valores de ram y swap:
        #total, available, percent, used, free, active, inactive, buffers, cached, shared

        #RAM
        texto = "*Uso de RAM: {}%*".format(ram.percent)
        texto += "\nTotal: {total} MB\nOcupado: {ocupado} MB\nLibre: {libre} MB".format(
            total=ram.total/1000000,
            ocupado=ram.used/1000000,
            libre=ram.free/1000000
        )

        #SWAP
        texto += "\n\n*Uso de SWAP: {}%*".format(swap.percent)
        texto += "\nTotal: {total} MB\nOcupado: {ocupado} MB\nLibre: {libre} MB".format(
            total=swap.total/1000000,
            ocupado=swap.used/1000000,
            libre=swap.free/1000000
        )

        bot.reply_to(message, texto, parse_mode="Markdown")


    @bot.message_handler(commands=["disco","disk"])
    def comm_disk(message):
        #Los comandos /disco y /disk proporcionan datos sobre el uso de disco (SD)
        print("Solicitado comando /disco")
        bot.send_chat_action(message.chat.id, "typing") #Mostrar estado "Escribiendo" por parte del bot
        particiones = psutil.disk_partitions()
        texto = "*--Particiones del sistema--*"
        
        for part in particiones:
            texto += "\n\n*{dev}* ({mountpoint}) {fstype}".format(
                dev=part.device,
                mountpoint=part.mountpoint,
                fstype=part.fstype
            )
            usage = psutil.disk_usage(part.mountpoint)
            texto += "\nTamaño: {total} MB\nOcupado: {ocupado} MB\nLibre: {libre} MB".format(
                #TODO Covertir a GB
                total=usage.total/1000000,
                ocupado=usage.used/1000000,
                libre=usage.free/1000000
            )
        
        bot.reply_to(message, texto, parse_mode="Markdown")


polling_thread = threading.Thread(target=bot_polling)
polling_thread.daemon = True
polling_thread.start()

while True:
    try:
        input()
    except KeyboardInterrupt:
        break


print("Ejecución finalizada!")
