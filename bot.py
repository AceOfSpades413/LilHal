import discord
from discord.ext import commands
import random
from classes.CardgameUtils import Card, Deck
import math
import json

client = commands.Bot(command_prefix='!', case_insensitive=True)
client.remove_command('help')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")
activeUsers=[]

servers={}

@client.event
async def on_guild_join(guild):
    if str(guild.id) not in servers:
        servers[str(guild.id)]={
            "users":{},
            "roles":{},
            "currencySymbol":'$',
            "serverWorkCooldown":120
        }

def initUserEconomy(user, guild):
    servers[str(guild.id)]["users"][str(user.id)]={
        "money":0,
        "bank":0,
        "workCooldown":0
    }

def modifyUserBalance(user, guild, amount):
    if str(user.id) not in servers[str(guild.id)]["users"]:
        initUserEconomy(user,guild)
    servers[str(guild.id)]["users"][str(user.id)]["money"]+=amount

def getUserCashBalance(user, guild):
    if str(user.id) not in servers[str(guild.id)]["users"]:
        initUserEconomy(user,guild)
    return servers[str(guild.id)]["users"][str(user.id)]["money"]

def getUserBankBalance(user, guild):
    if str(user.id) not in servers[str(guild.id)]["users"]:
        initUserEconomy(user,guild)
    return servers[str(guild.id)]["users"][str(user.id)]["bank"]



@client.command()
async def dumpJson(ctx):
    f = open("serverdata.json",'w')
    f.write(json.dumps(servers))
    f.close()

@client.command()
async def setCurrencySymbol(ctx, symbol):
    servers[str(ctx.message.guild.id)]["currencySymbol"]=str(symbol)

def getCurrencySymbol(ctx):
    return servers[str(ctx.message.guild.id)]["currencySymbol"]

@client.command()
async def bal(ctx):
    currencySymbol = servers[str(ctx.guild.id)]['currencySymbol']
    cash = getUserCashBalance(ctx.message.author, ctx.message.guild)
    bank = getUserBankBalance(ctx.message.author, ctx.message.guild)
    embed = discord.Embed(title=str(ctx.message.author) + "'s Balance")
    embed.add_field(name='Cash', value=currencySymbol + str(cash))
    embed.add_field(name='Bank', value=currencySymbol + str(bank))
    await ctx.send(embed=embed)
    return

@client.command()
async def bal(ctx, target: discord.Member):
    currencySymbol = servers[str(ctx.guild.id)]['currencySymbol']
    cash = getUserCashBalance(target, ctx.message.guild)
    bank = getUserBankBalance(target, ctx.message.guild)
    embed = discord.Embed(title=str(target) + "'s Balance")
    embed.add_field(name='Cash', value=currencySymbol + str(cash))
    embed.add_field(name='Bank', value=currencySymbol + str(bank))
    await ctx.send(embed=embed)
    return

@client.command()
async def work(ctx):
    amount = random.randint(50,200)
    modifyUserBalance(ctx.message.author, ctx.message.guild, amount)
    await ctx.send("You have made "+servers[str(ctx.message.guild.id)]["currencySymbol"]+str(amount))


@client.command()
async def pay(ctx, target: discord.Member, amount):
    try:
        amount=int(amount)
    except ValueError:
        await ctx.send("That is not a number")
        return
    if amount <=0:
        await ctx.send("You cannot pay someone a negative or zero value")
        return
    if amount > getUserCashBalance(ctx.message.author, ctx.message.guild):
        await ctx.send("You do not have enough cash")
        return
    modifyUserBalance(ctx.message.author, ctx.message.guild, -1*amount)
    modifyUserBalance(target, ctx.message.guild, amount)

@client.command()
async def rob(ctx, target: discord.Member):
    targetBalance=getUserCashBalance(target, ctx.message.guild)
    success = random.randint(0, 3)
    if success <= 2:
        transfer = (((random.randint(6, 9))/10)*targetBalance).__round__()
        modifyUserBalance(target, ctx.message.guild, -transfer)
        modifyUserBalance(ctx.message.author, ctx.message.guild, transfer)
        await ctx.send("you robbed "+ str(target)+ " for "+ getCurrencySymbol(ctx)+str(transfer))
    elif success >= 3:

        await ctx.send("you failed to rob and lost")
    return





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
    newembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/320338902747709452/699127157729001532/Chip.png")
    await messageID.edit(embed=newembed)



@client.event
async def on_ready():
    print("Bot Online!")
    await client.change_presence(activity=discord.Game(name="at the virtual casino"))
    f=open("serverdata.json",'r')
    datastring=f.readline().strip('\n')
    global servers
    servers=json.loads(datastring)
    print(datastring)


@client.command()
async def bj(ctx, money="failure"):
    if money=="failure": #checks if they are betting money
        await ctx.send("Proper usage: `!bj <bet amount>`")
        return
    money=float(money)
    if money<100 or money-math.trunc(money)!=0: #checks to see if there is a decimal
        await ctx.send("Bet amount must be an integer above 100")
        return
    if ctx.author in activeUsers:
        await ctx.send("You already have a game!")
        return
    if getUserCashBalance(ctx.author, ctx.guild)<money:
        await ctx.send("You do not have that much money")
        return
    money=int(money)
    modifyUserBalance(ctx.message.author, ctx.message.guild, -1*money)
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
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/320338902747709452/699127157729001532/Chip.png")

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
                move=response.content.lower()
            except: #forces stand here
                move="stand"

            if move=="hit":
                playerHand.append(deck.getRandomCard()) #gives player new card
                playerScore, playerString = updateStats(playerHand) #calculates players new card total
                newembed = discord.Embed(title="Blackjack: " + str(ctx.author)) #updates game message
                newembed.add_field(name="Player Hand", value=playerString + "\n\n" + "Your score: " + str(playerScore))
                #newembed.add_field(name="|", value="|")
                newembed.add_field(name="Dealer Hand", value=dealerString + "\n\n" + "Dealer's Score: " + str(dealerScore))
                newembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/320338902747709452/699127157729001532/Chip.png")
                await thisMessage.edit(embed=newembed)
                invalid = False
                moveCounterPlayer+=1
            elif move=="stand":
                stay= True
                invalid = False

    result=""
    if playerScore > 21: #if player busts
        dealerScore, dealerString = updateStats(dealerHand) #dealer flips card
        result = "BUST" #sets result msg to bust

    else:
        dealerScore, dealerString = updateStats(dealerHand)
        if playerScore==21 and dealerScore==21 and moveCounterPlayer==0 and moveCounterDealer==0:
            result = "TIE"
        if playerScore==21 and moveCounterPlayer==0 and (dealerScore<21 or moveCounterDealer>0):
            result="BLACKJACK"
        if dealerScore==21 and moveCounterDealer==0 and (playerScore<21 or moveCounterPlayer>0):
            result = "LOSS"

        while (dealerScore < playerScore and dealerScore < 21): #Dealer Hit, DO NOT EXCLUDE IF NOT BLACKJACK
            dealerHand.append(deck.getRandomCard())
            moveCounterDealer+=1
            dealerScore, dealerString = updateStats(dealerHand)

        if not result=="BLACKJACK" and not result =="LOSS":
            if dealerScore>21:
                result="WIN"
            elif (playerScore == dealerScore):
                result="TIE"
            elif (playerScore > dealerScore):
                result="WIN"
            elif (playerScore < dealerScore):
                result="LOSS"

    i=activeUsers.index(ctx.author) #finds player pos after game
    activeUsers.pop(i) #removes player after game ends based on pos
    if result == "BLACKJACK":
        winnings=money*2.5
        resultString = "Blackjack: +" + getCurrencySymbol(ctx) + str(int(money*1.5))
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.green())
    elif result == "WIN":
        winnings=money*2
        resultString = "Win: +"  + getCurrencySymbol(ctx) + str(money)
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.green())
    elif result == "TIE":
        winnings=money
        resultString = "Tie: +" + getCurrencySymbol(ctx) + str(0)
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.blue())
    elif result=="BUST" or result=="LOSS":
        winnings=0
        resultString="Loss: -" + getCurrencySymbol(ctx) + str(money)
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.red())
    modifyUserBalance(ctx.author, ctx.guild, int(winnings))



client.run(TOKEN)