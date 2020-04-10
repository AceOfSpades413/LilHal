import discord
from discord.ext import commands
import random
from classes.CardgameUtils import Card, Deck

client = commands.Bot(command_prefix='!')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")
activeUsers=[]


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

async def updateBJEmbed(messageID, ctx, playerString, dealerString, playerScore, dealerScore, result, color):
    if result=="":
        desc=""
    else:
        desc="Result: "+result
    newembed = discord.Embed(title="Blackjack: " + str(ctx.author), description=desc, color=color)
    newembed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
    # newembed.add_field(name="|", value="|")
    newembed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
    await messageID.edit(embed=newembed)

def updateStats(playerHand):
    score = calcScore(playerHand)
    playerString=""
    for card in playerHand:
        playerString+=str(card) + " "
    return score, playerString

@client.event
async def on_ready():
    print("Bot Online!")
    await client.change_presence(activity=discord.Game(name="at Andrew's virtual casino"))


@client.command()
async def bj(ctx):
    if ctx.author in activeUsers:
        await ctx.send("You already have a game!")
        return
    activeUsers.append(ctx.author)
    playerHand=[]
    dealerHand=[]
    playerScore=0
    dealerScore=0
    moveCounterDealer=0
    moveCounterPlayer=0
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
    #embed.add_field(name="|", value="|")
    embed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
    thisMessage = await ctx.send(embed=embed)
    stay=False
    while(playerScore<21 and stay == False):
        invalid = True
        while invalid:
            try:
                response = await client.wait_for('message', check = lambda message: message.author==ctx.author, timeout=30)
            except:#maybe player loses money here?
                await thisMessage.edit(embed=discord.Embed(title="Blackjack: " + str(ctx.author), description="GAME TIMEOUT"))
                i = activeUsers.index(ctx.author)
                activeUsers.pop(i)
                return

            if response.content.lower()=="hit":
                playerHand.append(deck.GetRandomCard())
                playerScore, playerString = updateStats(playerHand)
                newembed = discord.Embed(title="Blackjack: " + str(ctx.author))
                newembed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
                #newembed.add_field(name="|", value="|")
                newembed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
                await thisMessage.edit(embed=newembed)
                invalid = False
                moveCounterPlayer+=1
            elif response.content.lower()=="stand":
                stay= True
                invalid = False

    result=""
    if playerScore > 21:
        dealerScore, dealerString = updateStats(dealerHand)
        result = "LOSS"
        await updateBJEmbed(thisMessage,ctx,playerString, dealerString, playerScore, dealerScore, result, discord.Color.red())

    else:
        dealerScore, dealerString = updateStats(dealerHand)
        if playerScore==21 and dealerScore==21 and moveCounterPlayer==0 and moveCounterDealer==0:
            result = "TIE"
            await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, result,
                                discord.Color.blue())

        if playerScore==21 and moveCounterPlayer==0 and (dealerScore<21 or moveCounterDealer>0):
            result="BLACKJACK"
            await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, result,
                                discord.Color.green())

        if dealerScore==21 and moveCounterDealer==0 and (playerScore<21 or moveCounterPlayer>0):
            result = "LOSS"
            await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, result,
                                discord.Color.red())

        while (dealerScore < playerScore and dealerScore < 21): #Dealer Hit, DO NOT EXCLUDE IF NOT BLACKJACK
            dealerHand.append(deck.GetRandomCard())
            moveCounterDealer+=1
            dealerScore, dealerString = updateStats(dealerHand)

        if not result=="blackjack" and not result =="loss":
            if dealerScore>21:
                result="WIN"
                await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, result,
                                    discord.Color.green())

            elif (playerScore == dealerScore):
                result="TIE"
                await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, result,
                                    discord.Color.blue())
            elif (playerScore > dealerScore):
                result="WIN"
                await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, result,
                                    discord.Color.green())

            elif (playerScore < dealerScore):
                result="LOSS"
                await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, result,
                                    discord.Color.red())
    i=activeUsers.index(ctx.author)
    activeUsers.pop(i)




client.run(TOKEN)