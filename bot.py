import discord
from discord.ext import commands
import random
from classes.CardgameUtils import Card, Deck

client = commands.Bot(command_prefix='!')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")

def endGame(dealerScore, playerScore, ctx):
    if playerScore > dealerScore:
        return("You win!")
    elif playerScore < dealerScore:
        return("You lose.")
    else:
        return("You tied.")
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

@client.event
async def on_ready():
    print("Bot Online!")

@client.command()
async def bj(ctx):
    deck = Deck()
    playerHand = deck.deal(2)
    dealerHand = deck.deal(2)

    playerScore = calcScore(playerHand)
    embed = discord.Embed(title="Blackjack: "+ str(ctx.author))

    playerString = ""
    for card in playerHand:
        playerString += (str(card) + " ")

    dealerString=str(dealerHand[0])
    for i in range(len(dealerHand)-1):
        dealerString += "   ? "
    dealerScore = calcScore([dealerHand[0]])
    embed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
    embed.add_field(name="|", value="|")
    embed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
    await ctx.send(embed=embed)




client.run(TOKEN)



