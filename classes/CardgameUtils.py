import random

class Card:
    def __init__(self, value, suit):
        self.value=value
        self.suit=suit

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
    def __str__(self):
        return str(self.getCardFace()) + self.getSuit()

class Deck:
    def __init__(self):
        self.cards = []
        for i in range(2, 15):
            self.cards.append(Card(i, ":hearts:"))
            self.cards.append(Card(i, ":diamonds:"))
            self.cards.append(Card(i, ":spades:"))
            self.cards.append(Card(i, ":clubs:"))

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






