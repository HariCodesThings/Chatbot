from chatbot import *
from multiprocessing import Pool
import time

def parallel_run(bot):
    if bot.botnick == "two-bot":
        time.sleep(3)
    bot.run_bot()

bot1 = ChatBot(botnick="one")
bot2 = ChatBot(botnick="two")

time.sleep(3)

bot1.init_bot()
bot2.init_bot()

bot1.target = "two-bot"
bot2.target = "one-bot"

with Pool(2) as p:
    p.map(parallel_run, [bot1, bot2])



