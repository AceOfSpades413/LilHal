import discord
from discord.ext import commands
import random
from classes.CardgameUtils import Card, Deck

client = commands.Bot(command_prefix='!')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")
activeGames={}

def endGame(dealerScore, playerScore, ctx):
    if playerScore > dealerScore:
        return("You win!")
    elif playerScore < dealerScore:
        return("You lose.")
    else:
        return("You tied.")

def calcScore(cards):
    score = 0
    cardValueList=[]
    for card in cards:
        cardValueList.append(card.getNumberValue())
    cardValueList.sort()
    for val in cardValueList:
        if val<=10:
            score+=val
        elif val <=13:
            score+=10
        else:
            if score+11>21:
                score+=1
            else:
                score+=11


    return score

def updateStats(playerHand):
    score = calcScore(playerHand)
    playerString=""
    for card in playerHand:
        playerString+=str(card) + " "
    return score, playerString

@client.event
async def on_ready():
    print("Bot Online!")

@client.command()
async def test(ctx):
    await ctx.send("test")

@client.command()
async def bj(ctx):
    playerHand=[]
    dealerHand=[]
    playerScore=0
    dealerScore=0
    deck = Deck()
    playerHand = deck.deal(2)
    dealerHand = deck.deal(2)

    playerScore, playerString = updateStats(playerHand)
    embed = discord.Embed(title="Blackjack: "+ str(ctx.author))

    dealerString=str(dealerHand[0])
    for i in range(len(dealerHand)-1):
        dealerString += "   ? "
    dealerScore = calcScore([dealerHand[0]])
    embed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
    embed.add_field(name="|", value="|")
    embed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
    thisMessage = await ctx.send(embed=embed)
    stay=False
    while(playerScore<21 and stay == False):
        def check(author):
            def innerCheck(message):
                return message.author==author
        invalid = True
        while invalid:
            response = await client.wait_for('message', check=check(ctx.author), timeout=30)
            if response.content=="hit":
                playerHand.append(deck.GetRandomCard())
                playerScore, playerString = updateStats(playerHand)
                newembed = discord.Embed(title="Blackjack: " + str(ctx.author))
                newembed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
                newembed.add_field(name="|", value="|")
                newembed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
                await thisMessage.edit(embed=newembed)
                invalid = False
            elif response.content=="stand":
                stay= True
                invalid = False

        if playerScore > 21:
            dealerScore, dealerString = updateStats(dealerHand)
            newembed = discord.Embed(title="Blackjack: " + str(ctx.author), description="Result: BUST", color=discord.Color.dark_red())
            newembed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
            newembed.add_field(name="|", value="|")
            newembed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
            await thisMessage.edit(embed=newembed)
        else:
            dealerScore, dealerString = updateStats(dealerHand)
            while (dealerScore < playerScore and dealerScore<21):
                dealerHand.append(deck.GetRandomCard())
                dealerScore, dealerString = updateStats(dealerHand)
            newembed = discord.Embed(title="Blackjack: " + str(ctx.author), description="Result: LOSS",color=discord.Color.dark_red())
            newembed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
            newembed.add_field(name="|", value="|")
            newembed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
            await thisMessage.edit(embed=newembed)




@client.event
async def on_message(message):

    await client.process_commands(message)


client.run(TOKEN)