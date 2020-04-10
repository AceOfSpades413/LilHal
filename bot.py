import discord
from discord.ext import commands
import random
from classes.CardgameUtils import Card, Deck

client = commands.Bot(command_prefix='!')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")

@client.event
async def on_ready():
    print("Bot Online!")

@client.command()
async def bj(ctx):
    deck = Deck()
    playerHand = deck.deal(2)
    dealerHand = deck.deal(2)
    for x in playerHand:
        await ctx.send(x)







client.run(TOKEN)

def calcScore(cards):
    score = 0
    for card in cards:
        if card.getNumberValue() <=9:
            score+=card.getNumberValue()
        elif card.getNumberValue() <=13:
            score+=10
        elif card.getNumberValue() == 14:
            if score+11 > 21:
                score+=1
            else:
                score+=11
    return score

