import random
import sys

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        self.suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        random.shuffle(self.cards)
    
    def deal_card(self):
        if len(self.cards) == 0:
            self.reset()
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.bet = 0
        self.is_split_hand = False
        self.can_double = True
        self.insurance_bet = 0
        self.is_surrendered = False
    
    def add_card(self, card):
        self.cards.append(card)
        if len(self.cards) > 2:
            self.can_double = False
    
    def get_value(self):
        value = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                value += 11
            else:
                value += card.get_value()
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_bust(self):
        return self.get_value() > 21
    
    def is_soft_17(self):
        if self.get_value() != 17:
            return False
        
        # Check if we have at least one Ace counted as 11
        value = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                value += 11
            else:
                value += card.get_value()
        
        # If we have aces and our current value is 17, check if any ace is being counted as 11
        return aces > 0 and value >= 17
    
    def can_split(self):
        return (len(self.cards) == 2 and 
                self.cards[0].get_value() == self.cards[1].get_value() and
                not self.is_split_hand)
    
    def __str__(self):
        return ', '.join(str(card) for card in self.cards) + f" (Value: {self.get_value()})"

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hands = []
        self.dealer_hand = Hand()
        self.player_money = 1000
        self.current_hand_index = 0
        self.dealer_checked_blackjack = False
    
    def place_bet(self):
        while True:
            try:
                print(f"\nYour money: ${self.player_money}")
                bet = int(input("Place your bet: $"))
                if bet <= 0:
                    print("Bet must be positive!")
                elif bet > self.player_money:
                    print("You don't have enough money!")
                else:
                    return bet
            except ValueError:
                print("Please enter a valid number!")
    
    def deal_initial_cards(self):
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.dealer_checked_blackjack = False
        
        for _ in range(2):
            self.player_hands[0].add_card(self.deck.deal_card())
            self.dealer_hand.add_card(self.deck.deal_card())
    
    def offer_insurance(self):
        if self.dealer_hand.cards[0].rank == 'A':
            max_insurance = self.player_hands[0].bet // 2
            if max_insurance > 0 and self.player_money >= max_insurance:
                print(f"\nDealer is showing an Ace. Insurance available.")
                print(f"Insurance bet (up to ${max_insurance}) pays 2:1 if dealer has blackjack.")
                while True:
                    try:
                        choice = input("Place insurance bet? (y/n): ").lower().strip()
                        if choice == 'n':
                            return False
                        elif choice == 'y':
                            while True:
                                bet = int(input(f"Insurance bet amount (max ${max_insurance}): $"))
                                if bet <= 0:
                                    print("Insurance bet must be positive!")
                                elif bet > max_insurance:
                                    print(f"Insurance bet cannot exceed ${max_insurance}!")
                                elif bet > self.player_money:
                                    print("You don't have enough money!")
                                else:
                                    self.player_hands[0].insurance_bet = bet
                                    return True
                        else:
                            print("Please enter 'y' or 'n'!")
                    except ValueError:
                        print("Please enter a valid number!")
        return False
    
    def check_dealer_blackjack(self):
        dealer_upcard = self.dealer_hand.cards[0]
        if dealer_upcard.rank == 'A' or dealer_upcard.get_value() == 10:
            self.dealer_checked_blackjack = True
            return self.dealer_hand.is_blackjack()
        return False
    
    def handle_insurance_payout(self):
        if self.player_hands[0].insurance_bet > 0:
            if self.dealer_hand.is_blackjack():
                insurance_payout = self.player_hands[0].insurance_bet * 2
                print(f"Insurance wins! Payout: ${insurance_payout}")
                self.player_money += insurance_payout
            else:
                print(f"Insurance loses! Loss: ${self.player_hands[0].insurance_bet}")
                self.player_money -= self.player_hands[0].insurance_bet
    
    def offer_surrender(self, hand):
        dealer_upcard = self.dealer_hand.cards[0]
        
        if dealer_upcard.rank == 'A' and not self.dealer_checked_blackjack:
            print("Cannot surrender until dealer checks for blackjack with Ace showing.")
            return False
        
        choice = input("Surrender (forfeit half your bet)? (y/n): ").lower().strip()
        if choice == 'y':
            surrender_loss = hand.bet // 2
            print(f"Hand surrendered. Loss: ${surrender_loss}")
            self.player_money -= surrender_loss
            hand.is_surrendered = True
            return True
        return False
    
    def show_hands(self, hide_dealer_card=True):
        print(f"\nDealer's hand:")
        if hide_dealer_card and len(self.dealer_hand.cards) > 1:
            print(f"{self.dealer_hand.cards[0]}, [Hidden Card]")
        else:
            print(f"{self.dealer_hand}")
        
        if len(self.player_hands) == 1:
            print(f"\nYour hand: {self.player_hands[0]}")
        else:
            for i, hand in enumerate(self.player_hands):
                marker = " <-- Current" if i == self.current_hand_index else ""
                print(f"\nHand {i+1}: {hand}{marker}")
    
    def player_turn(self):
        for hand_index, hand in enumerate(self.player_hands):
            self.current_hand_index = hand_index
            
            if hand.is_blackjack():
                print(f"\nHand {hand_index + 1}: BLACKJACK!")
                continue
            
            first_action = True
            while not hand.is_bust() and not hand.is_surrendered:
                self.show_hands()
                
                if len(self.player_hands) > 1:
                    print(f"\nPlaying Hand {hand_index + 1}")
                
                actions = ['hit', 'stand']
                
                if first_action:
                    actions.append('surrender')
                
                if hand.can_double and self.player_money >= hand.bet:
                    actions.append('double')
                
                if hand.can_split() and self.player_money >= hand.bet:
                    actions.append('split')
                
                print(f"Actions: {', '.join(actions)}")
                action = input("What would you like to do? ").lower().strip()
                
                if action == 'hit':
                    hand.add_card(self.deck.deal_card())
                    print(f"You drew: {hand.cards[-1]}")
                    if hand.is_bust():
                        print("BUST! You went over 21!")
                        break
                
                elif action == 'stand':
                    break
                
                elif action == 'surrender' and first_action:
                    if self.offer_surrender(hand):
                        break
                
                elif action == 'double' and 'double' in actions:
                    hand.bet *= 2
                    hand.add_card(self.deck.deal_card())
                    print(f"You doubled down and drew: {hand.cards[-1]}")
                    break
                
                elif action == 'split' and 'split' in actions:
                    self.split_hand(hand_index)
                    break
                
                else:
                    print("Invalid action!")
                
                first_action = False
    
    def split_hand(self, hand_index):
        original_hand = self.player_hands[hand_index]
        new_hand = Hand()
        
        new_hand.add_card(original_hand.cards.pop())
        new_hand.bet = original_hand.bet
        new_hand.is_split_hand = True
        original_hand.is_split_hand = True
        
        
        original_hand.add_card(self.deck.deal_card())
        new_hand.add_card(self.deck.deal_card())
        
        self.player_hands.insert(hand_index + 1, new_hand)
        
        print("Hand split!")
    
    def dealer_turn(self):
        print(f"\nDealer reveals hidden card: {self.dealer_hand}")
        
        while self.dealer_hand.get_value() < 17 or self.dealer_hand.is_soft_17():
            card = self.deck.deal_card()
            self.dealer_hand.add_card(card)
            print(f"Dealer draws: {card}")
            print(f"Dealer's hand: {self.dealer_hand}")
        
        if self.dealer_hand.is_bust():
            print("Dealer busts!")
    
    def determine_winner(self):
        dealer_value = self.dealer_hand.get_value()
        dealer_blackjack = self.dealer_hand.is_blackjack()
        dealer_bust = self.dealer_hand.is_bust()
        
        total_winnings = 0
        
        for i, hand in enumerate(self.player_hands):
            hand_num = f"Hand {i+1}: " if len(self.player_hands) > 1 else ""
            
            if hand.is_surrendered:
                continue
            
            elif hand.is_bust():
                print(f"{hand_num}Player busts - Dealer wins! Loss: ${hand.bet}")
                total_winnings -= hand.bet
            
            elif hand.is_blackjack() and not dealer_blackjack:
                winnings = int(hand.bet * 1.5)
                print(f"{hand_num}Player BLACKJACK! Win: ${winnings}")
                total_winnings += winnings
            
            elif dealer_bust:
                print(f"{hand_num}Dealer busts - Player wins! Win: ${hand.bet}")
                total_winnings += hand.bet
            
            elif hand.get_value() > dealer_value:
                print(f"{hand_num}Player wins! Win: ${hand.bet}")
                total_winnings += hand.bet
            
            elif hand.get_value() < dealer_value:
                print(f"{hand_num}Dealer wins! Loss: ${hand.bet}")
                total_winnings -= hand.bet
            
            else:
                print(f"{hand_num}Push (tie)! Bet returned.")
        
        self.player_money += total_winnings
        
        if total_winnings > 0:
            print(f"\nTotal winnings: ${total_winnings}")
        elif total_winnings < 0:
            print(f"\nTotal losses: ${abs(total_winnings)}")
        else:
            print(f"\nNo money gained or lost.")
        
        print(f"Your money: ${self.player_money}")
    
    def play_round(self):
        if self.player_money <= 0:
            print("You're out of money! Game over.")
            return False
        
        bet = self.place_bet()
        
        self.deal_initial_cards()
        self.player_hands[0].bet = bet
        
        self.show_hands()
        
        insurance_offered = self.offer_insurance()
        
        dealer_has_blackjack = self.check_dealer_blackjack()
        
        if insurance_offered:
            self.handle_insurance_payout()
        
        if dealer_has_blackjack:
            print(f"\nDealer reveals: {self.dealer_hand}")
            print("Dealer has BLACKJACK!")
            
            if self.player_hands[0].is_blackjack():
                print("Both have BLACKJACK! It's a push!")
            else:
                print("You lose!")
                self.player_money -= bet
        elif self.player_hands[0].is_blackjack():
            print("BLACKJACK! You win!")
            self.player_money += int(bet * 1.5)
        else:
            self.player_turn()
            
            if not all(hand.is_bust() or hand.is_surrendered for hand in self.player_hands):
                self.dealer_turn()
            
            self.determine_winner()
        
        return True
    
    def play(self):
        print("Welcome to Blackjack!")
        print("Rules: Get closer to 21 than the dealer without going over.")
        print("Face cards = 10, Aces = 1 or 11, Number cards = face value")
        
        while True:
            if not self.play_round():
                break
            
            play_again = input("\nPlay another round? (y/n): ").lower().strip()
            if play_again != 'y':
                break
        
        print(f"Thanks for playing! Final money: ${self.player_money}")

if __name__ == "__main__":
    game = BlackjackGame()
    game.play()