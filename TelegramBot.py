#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Bot Telegram para proporcionar estadisticas del servidor RPi
"""

import telebot
import psutil
from time import sleep

bot = telebot.TeleBot("TOKEN") #Actualizar token

@bot.message_handler(commands=["start"])
def comm_start(message):
    #El comando /start da la bienvenida al bot
    bot.send_message(
        message.chat.id,
        "¡Hola!"
    )
    print("Solicitado comando /start")

@bot.message_handler(commands=["help"])
def comm_help(message):
    #El comando /help proporciona información de ayuida sobre cómo se usa el bot
    bot.send_message(
        message.chat.id,
        ""
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


#while True:
#    #Bucle para evitar que el bot finalice al detectarse un error
#    try:
#        print("Bot Polling iniciado")
#        bot.polling(
#            none_stop=True,
#            interval=1
#        )
#    except KeyboardInterrupt:
#        bot.stop_polling()
#        break
#    except Exception as ex:
#        print("Error en ejecución de polling:\n{}".format(ex))
#        print("Polling se reiniciara en 30 segundos")
#        sleep(30)

print("Bot Polling iniciado")
bot.polling(none_stop=True, interval=1)

print("Ejecución finalizada!")
