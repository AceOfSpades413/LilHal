import random
import discord

class Card:
    def __init__(self, value, suit, emojiDict):
        self.value=value
        self.suit=suit
        self.emojiDict=emojiDict

    def getSuit(self):
        return self.suit
    def getNumberValue(self):
        return self.value

    def getCardFace(self):
        if self.value==14:
            return 'A'
        elif self.value==13:
            return 'K'
        elif self.value==12:
            return 'Q'
        elif self.value==11:
            return 'J'
        else:
            return self.value

    def getEmojiText(self, emojiDict):
        return emojiDict[f"{self.getCardFace()}{self.getSuit()}"]

    def __str__(self):
        return self.getEmojiText(self.emojiDict)

class Deck:
    def __init__(self, emojiDict):
        self.cards = []
        for i in range(2, 15):
            self.cards.append(Card(i, "hearts", emojiDict))
            self.cards.append(Card(i, "diamonds", emojiDict))
            self.cards.append(Card(i, "spades", emojiDict))
            self.cards.append(Card(i, "clubs", emojiDict))

    def deal(self, num):
        cards = []
        for x in range(num):
            cards.append(self.getRandomCard())
        return cards

    def getRandomCard(self):
        pos = random.randint(0, len(self.cards) - 1)
        card=self.cards[pos]
        self.cards.pop(pos)
        return card

    def getCardsLeft(self):
        counter=0
        for card in self.cards:
            counter+=1
        return counter


class UnoCard:
    def __init__(self, value, color, emojiDict):
        if isinstance(value, str):
            if value == "skip":
                self.value= 10
            elif value == "reverse":
                self.value = 11
            elif value == "draw2":
                self.value = 12
            elif value == "wild":
                self.value = 13
            elif value == "wilddraw4":
                self.value = 14
        else:
            self.value=value
        self.color=color
        self.emojiDict=emojiDict

    def getColor(self):
        return self.color

    def getValue(self):
        if self.value==10:
            return "skip"
        elif self.value ==11:
            return "reverse"
        elif self.value==12:
            return "draw2"
        elif self.value==13:
            return "wild"
        elif self.value==14:
            return "wilddraw4"
        else:
            return self.value

    def getEmojiKey(self):
        return f"{self.getValue()}{self.getColor()}"

    def getEmojiText(self, emojiDict):
        return emojiDict[self.getEmojiKey()]

    def __str__(self):
        return self.getEmojiText(self.emojiDict)


class UnoDeck:
    def __init__(self, emojiDict):
        self.cards=[]
        colors=['red','yellow','green','blue']
        for i in range(12):
            for color in colors:
                if i==0:
                    self.cards.append(UnoCard(i,color,emojiDict))
                else:
                    self.cards.append(UnoCard(i, color,emojiDict))
                    self.cards.append(UnoCard(i, color,emojiDict))
        for i in range(4):
            self.cards.append(UnoCard("wild", "none",emojiDict))
            self.cards.append(UnoCard("wilddraw4", "none",emojiDict))

    def deal(self, num):
        cards = []
        for x in range(num):
            cards.append(self.getRandomCard())
        return cards

    def getRandomCard(self):
        pos = random.randint(0, len(self.cards) - 1)
        card=self.cards[pos]
        self.cards.pop(pos)
        return card

    def getCardsLeft(self):
        counter=0
        for card in self.cards:
            counter+=1
        return counter

    def getCards(self):
        return self.cards

class UnoPlayer:

    def __init__(self, user):
        self.cards=[]
        self.user=user
        self.handMessageId=""

    def setHandMessageId(self, newId):
        self.handMessageId = newId

    def addCards(self, cards):
        for card in cards:
            self.cards.append(card)

    def getUsername(self):
        return self.user.name

    def getUser(self):
        return self.user

    def getCards(self):
        cards=[]
        for card in self.cards:
            cards.append(card)
        return cards

    def getCardsLeft(self):
        return len(self.cards)

    #def playCard(self):

