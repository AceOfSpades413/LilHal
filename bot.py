import discord
from discord.ext import commands
import random
from classes.CardgameUtils import Card, Deck
import math

client = commands.Bot(command_prefix='!')
client.remove_command('help')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")
activeUsers=[]


def calcScore(cards):
    score = 0 #defines score as 0 to be recalculated
    cardValueList=[] #
    for card in cards: #
        cardValueList.append(card.getNumberValue())
    cardValueList.sort() #makes sure that aces are at the end of the calculation
    for val in cardValueList:
        if val<=10: #checks to see if card is a 2-10
            score+=val #adds the card number to the score
        elif val <=13: #checks to see if card is a J,Q, or K
            score+=10 #adds 10 to the score
        else: #realizes that card is an A
            if score+11>21: #checks to see if ace should be a 1 or an 11
                score+=1
            else:
                score+=11
    return score

def updateStats(Hand):
    score = calcScore(Hand) #calculates the score of what the user has
    String="" #resets the players string
    for card in Hand: #adds cards based on how many cards the player has
        String+=str(card) + " " #sets the players hand as the cards it has with spaces in between
    return score, String #returns players score and the list of cards it has

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



@client.event
async def on_ready():
    print("Bot Online!")
    await client.change_presence(activity=discord.Game(name="at the virtual casino"))


@client.command()
async def bj(ctx, money="failure"):
    if money=="failure": #checks if they are betting money
        await ctx.send("Proper usage: `!bj <bet amount>`")
        return
    if float(money)<=0 or float(money)-math.trunc(float(money))!=0: #checks to see if there is a decimal
        await ctx.send("Bet amount must be a non-zero positive integer")
        return
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
    playerHand = deck.deal(2) #gives player 2 cards
    dealerHand = deck.deal(2) #gives dealer 2 cards

    playerScore, playerString = updateStats(playerHand) #calculates score and makes it printable
    embed = discord.Embed(title="Blackjack: "+ str(ctx.author)) #prints game to chat

    dealerString=str(dealerHand[0]) #only shows the first card in dealers hand
    for i in range(len(dealerHand)-1):
        dealerString += "   ? "
    dealerScore = calcScore([dealerHand[0]]) #calculates the dealers entire score (1 card)
    embed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore)) #creates embed
    #embed.add_field(name="|", value="|")
    embed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore)) #creates embed
    thisMessage = await ctx.send(embed=embed) #pints out embed
    stay=False
    while(playerScore<21 and stay == False): #checks to see whether player has busted or is standing
        invalid = True
        while invalid: #checks to see if responded with hit/stay
            try:
                response = await client.wait_for('message', check = lambda message: message.author==ctx.author, timeout=30) #checks to see whether player sends msg within 30 secs
            except: #forces stand here
                await thisMessage.edit(embed=discord.Embed(title="Blackjack: " + str(ctx.author), description="GAME TIMEOUT"))
                i = activeUsers.index(ctx.author) #gets pos of player in list
                activeUsers.pop(i) #removes player based on pos
                return

            if response.content.lower()=="hit":
                playerHand.append(deck.getRandomCard()) #gives player new card
                playerScore, playerString = updateStats(playerHand) #calculates players new card total
                newembed = discord.Embed(title="Blackjack: " + str(ctx.author)) #updates game message
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
    if playerScore > 21: #if player busts
        dealerScore, dealerString = updateStats(dealerHand) #dealer flips card
        result = "BUST" #sets result msg to bust
        await updateBJEmbed(thisMessage,ctx,playerString, dealerString, playerScore, dealerScore, result, discord.Color.red()) #updates text

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
            dealerHand.append(deck.getRandomCard())
            moveCounterDealer+=1
            dealerScore, dealerString = updateStats(dealerHand)

        if not result=="BLACKJACK" and not result =="LOSS":
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
    i=activeUsers.index(ctx.author) #finds player pos after game
    activeUsers.pop(i) #removes player after game ends based on pos




client.run(TOKEN)