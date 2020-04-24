import discord
from discord.ext import commands, tasks
from classes.CardgameUtils import Card, Deck, UnoDeck, UnoCard, GamePlayer
import math, random
import json, copy
import asyncio

client = commands.Bot(command_prefix='!', case_insensitive=True)
client.remove_command('help')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")
activeUsers=[]

servers={}
emojiDict={}



def setUserKey(user, guild, key, value):
    servers[str(guild.id)]["users"][str(user.id)][key]=value

def getUserKey(user, guild, key):
    return servers[str(guild.id)]["users"][str(user.id)][key]

def getServerKey(guild, key):
    return servers[str(guild.id)][key]

def setServerKey(guild, key, value):
    servers[str(guild.id)][key]=value

def initUserEconomy(user, guild):
    servers[str(guild.id)]["users"][str(user.id)]={
        "money":0,
        "bank":0,
        "workCooldown":0,
        "robCooldown":0,
        "inventory":{}
    }

def modifyUserCashBalance(user, guild, amount):
    if str(user.id) not in servers[str(guild.id)]["users"]:
        initUserEconomy(user,guild)
    servers[str(guild.id)]["users"][str(user.id)]["money"]+=amount

def modifyUserBankBalance(user, guild, amount):
    if str(user.id) not in servers[str(guild.id)]["users"]:
        initUserEconomy(user,guild)
    servers[str(guild.id)]["users"][str(user.id)]["bank"]+=amount

def getUserCashBalance(user, guild):
    if str(user.id) not in servers[str(guild.id)]["users"]:
        initUserEconomy(user,guild)
    return servers[str(guild.id)]["users"][str(user.id)]["money"]

def getUserBankBalance(user, guild):
    if str(user.id) not in servers[str(guild.id)]["users"]:
        initUserEconomy(user,guild)
    return servers[str(guild.id)]["users"][str(user.id)]["bank"]

def getCurrencySymbol(guild):
    return servers[str(guild.id)]["currencySymbol"]

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

def updateStats(Hand):
    score = calcScore(Hand) #calculates the score of what the user has
    String="" #resets the players string
    for card in Hand: #adds cards based on how many cards the player has
        String+=str(card) + " " #sets the players hand as the cards it has with spaces in between
    return score, String #returns players score and the list of cards it has

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

def calcHand(cards, pot):
    for i in pot:
        cards.append(i)
    cardSymbols = []
    for i in cards:
        count=0
        for e in i:
            if (count == 2 or count == 3):
                print (e)
                cardSymbols.append(e)
            count+=1
    cardList={
        {
            
        }
    }






@client.event
async def on_ready():
    print("Bot Online!")
    await client.change_presence(activity=discord.Game(name="at the virtual casino"))
    try:
        serverdata=open("serverdata.json",'r')
    except:
        serverdata=open("serverdata.json", "w")
        serverdata.write('{}')
        serverdata.close()
        serverdata=open("serverdata.json",'r')
    global servers
    servers=json.load(serverdata)
    dumpJson.start()
    timeUpdates.start()
    try:
        emojidata=open("emojidata.json",'r')
    except:
        emojidata=open("emojidata.json", "w")
        emojidata.write('{}')
        emojidata.close()
        emojidata=open("emojidata.json",'r')
    global emojiDict
    emojiDict=json.load(emojidata)
    guildCheck.start()

@client.event
async def on_guild_join(guild):
    if str(guild.id) not in servers:
        servers[str(guild.id)]={
            "users":{},
            "roles":{},
            "currencySymbol":'$',
            "serverWorkCooldown":120,
            "serverRobCooldown":180,
            "serverInventory":{}
        }

@client.event
async def on_guild_remove(guild):
    del servers[str(guild.id)]

@client.event
async def on_message(message):
    if "lil hal" in message.content.lower() or "lilhal" in message.content.lower():
        response = "```diff\n" + """- It seems you have asked about DS's chat client auto-responder. This is an application designed to simulate DS's otherwise inimitably rad typing style, 
tone, cadence, personality, and substance of retort while he is away from the computer. The algorithms are guaranteed to be 9X% indistinguishable 
from DS's native neurological responses, based on some statistical analysis I basically just pulled out of my ass right now.```""".replace('\n','')
        await message.channel.send(response)

    await client.process_commands(message)



@client.command()
async def shop(ctx, page=1):
    await ctx.send("Not implemented")

@client.command()
async def buy(ctx):
    await ctx.send("Not implemented")

@client.command()
async def sell(ctx): #needs to be discussed for
    await ctx.send("Not implemented")






@tasks.loop(seconds=1.0)
async def dumpJson():
    f = open("serverdata.json",'w')
    f.write(json.dumps(servers, indent=4))
    f.close()

@tasks.loop(seconds=1.0)
async def timeUpdates():
    for serverid, serverdata in servers.items():
        for userid, userdata in serverdata['users'].items():
            #start operating on each value per user per server
            if(userdata["workCooldown"]>0):
                userdata["workCooldown"]-=1
            if(userdata["robCooldown"])>0:
                userdata["robCooldown"]-=1

@tasks.loop(seconds=1.0)
async def guildCheck():
    for guild in client.guilds:
        if str(guild.id) not in servers:
            servers[str(guild.id)] = {
                "users": {},
                "roles": {},
                "currencySymbol": '$',
                "serverWorkCooldown": 120,
                "serverRobCooldown": 180,
                "serverInventory": {}
            }

@client.command()
async def setCurrencySymbol(ctx, symbol):
    servers[str(ctx.message.guild.id)]["currencySymbol"]=str(symbol)

@client.command()
async def userinfo(ctx, *args):
    target = ""
    if len(args) == 0:
        target = ctx.author
    elif len(args) == 1:
        mc = discord.ext.commands.MemberConverter()
        try:
            target = await mc.convert(ctx, args[0])
        except:
            await ctx.send("user not found!")
            return
    else:
        await ctx.send("Improper command usage!")
        return
    embed=discord.Embed(title=str(target))
    embed.set_thumbnail(url=str(target.avatar_url))
    embed.add_field(name="Member of this server since:", value=target.joined_at)
    embed.add_field(name="Net worth: ", value=getCurrencySymbol(ctx.guild)+' '+str(getUserCashBalance(target, ctx.guild)+getUserBankBalance(target, ctx.guild)))
    embed.add_field(name="Work Cooldown:", value = getUserKey(ctx.author, ctx.guild, 'workCooldown'))
    await ctx.send(embed=embed)

@client.command()
async def bal(ctx, *args):
    target=""
    if len(args)==0:
        target=ctx.author
    elif len(args)==1:
        mc=discord.ext.commands.MemberConverter()
        try:
            target=await mc.convert(ctx, args[0])
        except:
            await ctx.send("user not found!")
            return
    else:
        await ctx.send("Improper command usage!")
        return
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
    cooldown = getUserKey(ctx.author, ctx.guild, 'workCooldown')
    if cooldown<=0:
        amount = random.randint(50,200)
        modifyUserCashBalance(ctx.message.author, ctx.message.guild, amount)
        await ctx.send("You have made "+servers[str(ctx.message.guild.id)]["currencySymbol"]+str(amount))
        setUserKey(ctx.author, ctx.guild, 'workCooldown', getServerKey(ctx.guild, 'serverWorkCooldown'))
    else:
        await ctx.send(f"You must wait {cooldown} seconds")

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
    modifyUserCashBalance(ctx.message.author, ctx.message.guild, -1*amount)
    modifyUserCashBalance(target, ctx.message.guild, amount)

@client.command()
async def rob(ctx, target: discord.Member):
    targetBalance=getUserCashBalance(target, ctx.message.guild)
    success = random.randint(0, 3)
    cooldown = getUserKey(ctx.author, ctx.guild, 'robCooldown')
    if cooldown <= 0:
        if success <= 2:
            transfer = (((random.randint(6, 9)) / 10) * targetBalance).__round__()
            modifyUserCashBalance(target, ctx.message.guild, -transfer)
            modifyUserCashBalance(ctx.message.author, ctx.message.guild, transfer)
            await ctx.send("you robbed " + str(target) + " for " + getCurrencySymbol(ctx.guild) + str(transfer))
        elif success >= 3:

            await ctx.send("you failed to rob and lost")
        setUserKey(ctx.author, ctx.guild, 'robCooldown', getServerKey(ctx.guild, 'serverRobCooldown'))
    else:
        await ctx.send(f"You must wait {cooldown} seconds")

@client.command()
async def dep(ctx, amount):
    if amount == ("all").lower():
        transfer = getUserCashBalance(ctx.author, ctx.guild)
    else:
        transfer = int(amount)
    balance = getUserCashBalance(ctx.author, ctx.guild)
    if balance >= transfer and transfer > 0:
        modifyUserCashBalance(ctx.author, ctx.guild, -transfer)
        modifyUserBankBalance(ctx.author, ctx.guild, transfer)
    elif balance < transfer:
        await ctx.send("you don't have enough money in your bank account to do that")
    else:
        await ctx.send("you can't deposit negative or zero amounts")
    return

@client.command(aliases=['with'])
async def withdraw(ctx, amount):
    if amount == ("all").lower():
        transfer = getUserBankBalance(ctx.author, ctx.guild)
    else:
        transfer = int(amount)
    balance = getUserBankBalance(ctx.author, ctx.guild)
    if balance >= transfer and transfer > 0:
        modifyUserBankBalance(ctx.author, ctx.guild, -transfer)
        modifyUserCashBalance(ctx.author, ctx.guild, transfer)
    elif balance < transfer:
        await ctx.send("you don't have enough money in your bank account to do that")
    else:
        await ctx.send("you can't withdraw negative or zero amounts")
    return

@client.command(aliases=['leaderboard', 'leaders'])
async def lb(ctx):
    lists = []
    for userid in servers[str(ctx.guild.id)]["users"]:
        mc = discord.ext.commands.MemberConverter()
        username=await mc.convert(ctx, userid)
        amount = getUserCashBalance(username, ctx.guild) + getUserBankBalance(username, ctx.guild)
        lists.append([amount, username.name])
        #await ctx.send(str(username) + " has " + str(symbol) + str(amount))
    count = 0
    lists.sort()
    lists.reverse()
    symbol = getCurrencySymbol(ctx.guild)
    embed=discord.Embed(title="Leaderboards")
    leaderString=""
    while count < len(lists):
        leaderString+="#"+str(count+1) + " " + str(lists[count][1]) + " - " + symbol + str(lists[count][0])+"\n"
        count+=1
    embed.add_field(name="Leaders", value=leaderString)
    await ctx.send(embed=embed)



async def gameStart(gamename, emoji, maxPlayers, ctx):

    embed = discord.Embed(title=f"{gamename}", description=f"Started by {ctx.author}")
    thisMessage = await ctx.send(embed=embed)
    await thisMessage.add_reaction(emoji)
    players = []
    for i in range(10, 0, -1):
        players = []
        thisMessage = await ctx.fetch_message(thisMessage.id)
        newEmbed = discord.Embed(title=f"{gamename}", description=f"Started by {ctx.author}")
        newEmbed.set_footer(text=f"{i} seconds left to sign up")
        for reaction in thisMessage.reactions:
            async for user in reaction.users():
                if user not in players and user != client.user:
                    players.append(user)
        if len(players) > 0:
            playerString = ""
            for player in players:
                playerString += f"{player.name}\n"

            newEmbed.add_field(name="Players", value=playerString, inline=False)

        await thisMessage.edit(embed=newEmbed)
        await asyncio.sleep(1)
    if len(players) <= 1:
        newEmbed = embed
        newEmbed.set_footer(text="Nobody wants to play!")
    else:
        newEmbed.set_footer(text="Sign up complete... wait for game!")
        await thisMessage.edit(embed=newEmbed)
        return players

@client.command()
async def uno(ctx):
    try:
        players=await gameStart("Uno", "<:W4:702235282556059719>", 8, ctx)
    except:
        return

    deck = UnoDeck(emojiDict)
    playerObjects=[]
    for player in players:
        currentPlayer=GamePlayer(player)
        playerObjects.append(currentPlayer)
        currentPlayer.addCards(deck.deal(7))
        playerEmbed=discord.Embed(title="Uno")
        handString=""
        for card in currentPlayer.getCards():
            handString+=str(card)
        playerEmbed.add_field(name="Your Hand:", value=handString)
        currentPlayer.setHandMessageId(await player.send(embed=playerEmbed))

    playedCards=[]
    playedCards.append(deck.getRandomCard())
    won=False
    playerCounter = 0
    publicEmbed = discord.Embed(title="Uno Game")
    publicEmbed.add_field(name="Current Card:", value=playedCards[len(playedCards) - 1])

    playerString = ""
    for player in playerObjects:
        thingepic = ""
        if (player) == playerObjects[playerCounter]:
            thingepic = "**>**"
        playerString += f"{thingepic}{player.getUsername()}: {player.getCardsLeft()}\n"
    publicEmbed.add_field(name="Player List/Cards Left:", value=playerString)
    publicMessage = await ctx.send(embed=publicEmbed)
    while not won:
        currentCard=playedCards[len(playedCards) - 1]

        # Begin player specific shit
        for player in playerObjects:
            if playerObjects.index(player)==playerCounter:
                playerEmbed=copy.copy(publicEmbed)
                currentMessage = await player.getUser().send(embed=playerEmbed)
                evaluatedCards=[]
                notPlayableCards=[]
                for card in player.getCards():
                    if card not in evaluatedCards:
                        if card.getColor()==currentCard.getColor() or card.getValue()== card.getValue() or card.getValue in ["wild", "wilddraw4"]:
                            evaluatedCards.append(card)
                        else:
                            notPlayableCards.append(card)
                for card in evaluatedCards:
                    await currentMessage.add_reaction(str(card))
                unplayableString=""
                for card in notPlayableCards:
                    unplayableString+=str(card)
                playerEmbed.add_field(name="Unplayable Cards:", value=unplayableString)



        playerCounter+=1


        # Update Public Embed
        publicEmbed=discord.Embed(title="Uno Game")
        publicEmbed.add_field(name="Current Card:", value=playedCards[len(playedCards)-1])

        playerString=""
        for player in playerObjects:
            thingepic=""
            if(player)==playerObjects[playerCounter]:
                thingepic="**>**"
            playerString+=f"{thingepic}{player.getUsername()}: {player.getCardsLeft()}\n"
        publicEmbed.add_field(name="Player List/Cards Left:", value=playerString)
        await publicMessage.edit(embed=publicEmbed)

        if playerCounter==len(playerObjects):
            won=True



@client.command(aliases=['pkr'])
async def poker(ctx, buyIn="no buy in"):
    if buyIn == "no buy in":
        await ctx.send("no buy in specified")
        return
    else:
        print(buyIn)
    try:
        players = await gameStart(f"Poker\t\tbuy in:{buyIn}", "<:AS:702234100836335636>", 8, ctx)
    except:
        return
    deck = Deck(emojiDict)
    potCards=[]
    playerObjects = []
    print (players)

    for player in players:
        currentPlayer = GamePlayer(player)
        playerObjects.append(currentPlayer)
        currentPlayer.addCards(deck.deal(2))
        playerEmbed = discord.Embed(title=f"Poker\t\tchips: {buyIn}")
        handString = ""
        handList = []
        for card in currentPlayer.getCards():
            handList.append(str(card))
        calcHand(handList, potCards)
        for i in handList:
            handString+=i
        playerEmbed.add_field(name="Your Hand:", value=handString)
        currentPlayer.setHandMessageId(await player.send(embed=playerEmbed))









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
    modifyUserCashBalance(ctx.message.author, ctx.message.guild, -1*money)
    activeUsers.append(ctx.author)
    playerHand=[]
    dealerHand=[]
    playerScore=0
    dealerScore=0
    moveCounterDealer=0
    moveCounterPlayer=0
    deck = Deck(emojiDict)
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
        resultString = "Blackjack: +" + getCurrencySymbol(ctx.guild) + str(int(money*1.5))
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.green())
    elif result == "WIN":
        winnings=money*2
        resultString = "Win: +"  + getCurrencySymbol(ctx.guild) + str(money)
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.green())
    elif result == "TIE":
        winnings=money
        resultString = "Tie: +" + getCurrencySymbol(ctx.guild) + str(0)
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.blue())
    elif result=="BUST" or result=="LOSS":
        winnings=0
        resultString="Loss: -" + getCurrencySymbol(ctx.guild) + str(money)
        await updateBJEmbed(thisMessage, ctx, playerString, dealerString, playerScore, dealerScore, resultString,
                            discord.Color.red())
    modifyUserCashBalance(ctx.author, ctx.guild, int(winnings))

@client.command()
async def hug(ctx):
    await ctx.send("plug!")
    return

client.run(TOKEN)