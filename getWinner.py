import random
import itertools

class Poker:
    def __init__(self):
        self.deck = [
            "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks", "As",
            "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc", "Ac",
            "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh", "Ah",
            "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd", "Ad",
            ]
        self.board = []
        self.players = []
        self.info = []
        random.shuffle(self.deck)
        
    def getWinner(self):
        topHand = []
        for i in self.info:
            print(i)
            if topHand == []:
                topHand.append(i)
                continue
            if i[1] > topHand[0][1]:
                topHand = []
                topHand.append(i)
                continue
            if i[1] == topHand[0][1]:
                topHand.append(i)
        if len(topHand) == 1:
            print("Player " + str(topHand[0][3]) + " wins! -> " + str(topHand[0][0]) + ": " + str(topHand[0][2]))
            return
        self.handleTie(topHand)
    
    def handleTie(self, hands):
        allRanks = []
        for hand in hands:
            allRanks.append([card[0] for card in hand[2]])

        if all(ranks == allRanks[0] for ranks in allRanks):
            splitPlayers = " ".join(str(hand[3]) for hand in hands)
            print("players: " + splitPlayers + " split")
            return
        winner = self.bestOfDupeHandRanking(hands) # different hands, reuse bestOfDupeHandRanking function to get the best hand
        print("Player " + str(winner[3]) + " wins! -> " + str(winner[0]) + ": " + str(winner[2]))
        return

    
    def checkIfGreater(self, card1, card2):
        card1Rank = self.cardRankToNumber(card1)
        card2Rank = self.cardRankToNumber(card2)
        if card1Rank > card2Rank:
            return 1
        elif card1Rank == card2Rank:
            return 2
        return 3
    
    def bestOfDupeHandRanking(self, hands):
        best = []
        if len(hands) == 1:
            return hands[0]
        for hand in hands:
            if best == []:
                best = hand
                continue
            for i in range(len(hand[2])):
                betterHand = self.checkIfGreater(hand[2][i][0], best[2][i][0])
                if betterHand == 1:
                    best = hand
                    break
                if betterHand == 3:
                    break
        return best
        
        
    def dealHands(self, num):
        players = []
        for _ in range(num):
            players.append([])
        for i in range(len(players)*2):
            players[i%num].append(self.deck.pop())
        self.players = players
        for i in range(8):
            if i == 0 or i == 4 or i == 6: # burn cards
                self.deck.pop()
            else:
                self.board.append(self.deck.pop())
        self.play()
        
    def play(self):
        for i in range(len(self.players)):
            cards = self.players[i] + self.board
            combinations = itertools.combinations(cards, 5)
            self.info.append(self.getBestHand(list(combinations), i))
        self.getWinner()
            
    def getBestHand(self, combos, i):
        val = 0
        bests = []
        for cards in combos:
            suit = {"s": [], "c" : [], "h": [], "d": []}
            num = {"2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "T": [], "J": [], "Q": [], "K": [], "A": [], }
            for card in cards:
                num[card[0]].append(card[1])
                suit[card[1]].append(card[0])
            result = self.getPokerHandRanking(cards, suit, num)
            if result[1] > val:
                bests = []
                val = result[1]
                result.append(i)
                result = self.organizeHand(result)
                bests.append(result)
                continue
            if result[1] == val:
                result.append(i)
                result = self.organizeHand(result)
                bests.append(result)
        return self.bestOfDupeHandRanking(bests)
                
    def organizeHand(self, info):
        cards = info[2]
        order = '23456789TJQKA'

        # ace low straight
        if info[1] == 5 or info[1] == 9 and any(card[0] == 'A' for card in cards) or any(card[0] == '2' for card in cards):
            order = 'A23456789TJQK'
        
        val = {rank: index for index, rank in enumerate(order)}
        sortedCards = sorted(cards, key=lambda card: val[card[0]], reverse=True)
        rank_count = {}
        for card in sortedCards:
            rank = card[0]
            rank_count[rank] = rank_count.get(rank, 0) + 1
        
        # move groups to the front
        sortedCards = sorted(sortedCards, key=lambda card: (rank_count[card[0]], val[card[0]]), reverse=True)
        info[2] = sortedCards
        
        return info
            
            
    def getPokerHandRanking(self, cards, suit, num):
        flush = False
        result = []
        for i in suit:
            if len(suit[i]) < 5:
                break
            flush = True
            if {'T', 'J', 'Q', 'K', 'A'}.issubset(suit[i]):
                return ["Royal Flush", 10, cards]
            if self.checkStraight(suit[i]):
                return ["Straight Flush", 9, cards]
        pair = 0
        three = 0
        for i in num:
            if len(num[i]) == 4:
                return ["Quads", 8, cards]
            if len(num[i]) == 3:
                three += 1
            if len(num[i]) == 2:
                pair += 1
        if pair > 0 and three > 0 :
            return ["Full House", 7, cards]
        if flush:
            return ["Flush", 6, cards]
        if self.checkStraight(cards):
            return ["Straight", 5, cards]
        if three > 0:
            return ["Set", 4, cards]
        if pair > 1:
            return ["Two Pair", 3, cards]
        if pair > 0:
            return ["Pair", 2, cards]
        return ["High Card", 1, cards]
    
    def cardRankToNumber(self, rank):
        rankToNum = {
            "A": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "X": 14,
        }
        return rankToNum[rank]
                    
            
    def checkStraight(self, cards):
        ranks = []
        for i in cards:
            ranks.append(i[0])
            if i[0] == "A":
                ranks.append("X")
        cards = ranks
        cards = [self.cardRankToNumber(letter) for letter in cards]
        cards.sort()
        for i in range(len(cards)-4):
            if cards[i] == cards[i+1]-1 and cards[i+1] == cards[i+2]-1 and cards[i+2] == cards[i+3]-1 and cards[i+3] == cards[i+4]-1:
                return True
        return False
    
    def test(self, cards):
        self.info.append(['Set', 4, ['6d', '6s', '6c', '9h', '8d'], 0])
        self.info.append(['Set', 4, ['6h', '6s', '6c', '9h', '7d'], 6])
        print(self.info)
        self.getWinner()
        
if __name__ == "__main__":
    poker = Poker()
    #poker.test(['5c', '5h', '5d', 'As', 'Ac'])
    poker.dealHands(10)