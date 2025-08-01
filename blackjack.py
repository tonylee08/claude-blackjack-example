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
        if len(self.cards) != 2:
            return False
        
        # Allow splitting pairs of same rank (e.g., A-A, 8-8)
        if self.cards[0].rank == self.cards[1].rank:
            return True
        
        # Allow splitting any 10-value cards (10, J, Q, K)
        return (self.cards[0].get_value() == 10 and 
                self.cards[1].get_value() == 10)
    
    def __str__(self):
        return ', '.join(str(card) for card in self.cards) + f" (Value: {self.get_value()})"

class PlayerActions:
    def __init__(self, game):
        self.game = game
    
    def hit(self, hand):
        hand.add_card(self.game.deck.deal_card())
        print(f"You drew: {hand.cards[-1]}")
        if hand.is_bust():
            print("BUST! You went over 21!")
            return True
        return False
    
    def stand(self, hand):
        return True
    
    def double_down(self, hand):
        additional_bet = hand.bet
        if self.game.player_money < additional_bet:
            print(f"Not enough money to double down! You need ${additional_bet} more.")
            return False
        
        self.game.player_money -= additional_bet
        hand.bet *= 2
        hand.add_card(self.game.deck.deal_card())
        print(f"You doubled down and drew: {hand.cards[-1]}")
        return True
    
    def split(self, hand_index):
        original_hand = self.game.player_hands[hand_index]
        additional_bet = original_hand.bet
        
        if self.game.player_money < additional_bet:
            print(f"Not enough money to split! You need ${additional_bet} more.")
            return False
        
        self.game.player_money -= additional_bet
        new_hand = Hand()
        
        # Move the second card to the new hand
        second_card = original_hand.cards.pop(1)
        new_hand.add_card(second_card)
        new_hand.bet = original_hand.bet
        new_hand.is_split_hand = True
        original_hand.is_split_hand = True
        
        # Deal one new card to each hand automatically
        original_hand.add_card(self.game.deck.deal_card())
        new_hand.add_card(self.game.deck.deal_card())
        
        self.game.player_hands.insert(hand_index + 1, new_hand)
        print("Hand split!")
        return True
    
    def surrender(self, hand):
        dealer_upcard = self.game.dealer_hand.cards[0]
        
        if dealer_upcard.rank == 'A' and not self.game.dealer_checked_blackjack:
            print("Cannot surrender until dealer checks for blackjack with Ace showing.")
            return False
        
        choice = input("Surrender (forfeit half your bet)? (y/n): ").lower().strip()
        if choice == 'y':
            surrender_return = hand.bet // 2
            print(f"Hand surrendered. Loss: ${hand.bet - surrender_return}")
            self.game.player_money += surrender_return
            hand.is_surrendered = True
            return True
        return False

class DealerActions:
    def __init__(self, game):
        self.game = game
    
    def reveal_card(self):
        print(f"\nDealer reveals hidden card: {self.game.dealer_hand}")
    
    def play_turn(self):
        self.reveal_card()
        
        while self.game.dealer_hand.get_value() < 17 or (self.game.dealer_hand.get_value() == 17 and self.game.dealer_hand.is_soft_17()):
            card = self.game.deck.deal_card()
            self.game.dealer_hand.add_card(card)
            print(f"Dealer draws: {card}")
            print(f"Dealer's hand: {self.game.dealer_hand}")
        
        if self.game.dealer_hand.is_bust():
            print("Dealer busts!")
    
    def check_blackjack(self):
        dealer_upcard = self.game.dealer_hand.cards[0]
        if dealer_upcard.rank == 'A' or dealer_upcard.get_value() == 10:
            self.game.dealer_checked_blackjack = True
            return self.game.dealer_hand.is_blackjack()
        return False

class GameFlow:
    def __init__(self, game):
        self.game = game
    
    def place_bet(self):
        while True:
            try:
                print(f"\nYour money: ${self.game.player_money}")
                bet = int(input("Place your bet: $"))
                if bet <= 0:
                    print("Bet must be positive!")
                elif bet > self.game.player_money:
                    print("You don't have enough money!")
                else:
                    return bet
            except ValueError:
                print("Please enter a valid number!")
    
    def deal_initial_cards(self):
        self.game.player_hands = [Hand()]
        self.game.dealer_hand = Hand()
        self.game.dealer_checked_blackjack = False
        
        for _ in range(2):
            self.game.player_hands[0].add_card(self.game.deck.deal_card())
            self.game.dealer_hand.add_card(self.game.deck.deal_card())
    
    def offer_insurance(self):
        if self.game.dealer_hand.cards[0].rank == 'A':
            insurance_amount = self.game.player_hands[0].bet // 2
            if insurance_amount > 0 and self.game.player_money >= insurance_amount:
                print(f"\nDealer is showing an Ace. Insurance available.")
                print(f"Insurance bet is exactly ${insurance_amount} (half your original bet) and pays 2:1 if dealer has blackjack.")
                while True:
                    choice = input("Place insurance bet? (y/n): ").lower().strip()
                    if choice == 'n':
                        return False
                    elif choice == 'y':
                        self.game.player_hands[0].insurance_bet = insurance_amount
                        return True
                    else:
                        print("Please enter 'y' or 'n'!")
        return False
    
    def handle_insurance_payout(self):
        if self.game.player_hands[0].insurance_bet > 0:
            if self.game.dealer_hand.is_blackjack():
                insurance_payout = self.game.player_hands[0].insurance_bet * 2
                print(f"Insurance wins! Payout: ${insurance_payout}")
                self.game.player_money += insurance_payout
            else:
                print(f"Insurance loses! Loss: ${self.game.player_hands[0].insurance_bet}")
                self.game.player_money -= self.game.player_hands[0].insurance_bet
    
    def determine_winner(self):
        dealer_value = self.game.dealer_hand.get_value()
        dealer_blackjack = self.game.dealer_hand.is_blackjack()
        dealer_bust = self.game.dealer_hand.is_bust()
        
        total_winnings = 0
        
        for i, hand in enumerate(self.game.player_hands):
            hand_num = f"Hand {i+1}: " if len(self.game.player_hands) > 1 else ""
            
            if hand.is_surrendered:
                continue
            
            elif hand.is_bust():
                print(f"{hand_num}Player busts - Dealer wins! Loss: ${hand.bet}")
                # Player loses their bet (already deducted when placed)
            
            elif hand.is_blackjack() and not dealer_blackjack:
                winnings = int(hand.bet * 1.5)
                print(f"{hand_num}Player BLACKJACK! Win: ${winnings}")
                self.game.player_money += hand.bet + winnings  # Return bet + blackjack bonus
                total_winnings += winnings
            
            elif dealer_bust:
                print(f"{hand_num}Dealer busts - Player wins! Win: ${hand.bet}")
                self.game.player_money += hand.bet * 2  # Return bet + equal winnings
                total_winnings += hand.bet
            
            elif hand.get_value() > dealer_value:
                print(f"{hand_num}Player wins! Win: ${hand.bet}")
                self.game.player_money += hand.bet * 2  # Return bet + equal winnings
                total_winnings += hand.bet
            
            elif hand.get_value() < dealer_value:
                print(f"{hand_num}Dealer wins! Loss: ${hand.bet}")
                # Player loses their bet (already deducted when placed)
            
            else:
                print(f"{hand_num}Push (tie)! Bet returned.")
                self.game.player_money += hand.bet  # Return bet only
        
        if total_winnings > 0:
            print(f"\nTotal winnings: ${total_winnings}")
        elif total_winnings < 0:
            print(f"\nTotal losses: ${abs(total_winnings)}")
        
        print(f"Your money: ${self.game.player_money}")

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hands = []
        self.dealer_hand = Hand()
        self.player_money = 1000
        self.current_hand_index = 0
        self.dealer_checked_blackjack = False
        
        self.player_actions = PlayerActions(self)
        self.dealer_actions = DealerActions(self)
        self.game_flow = GameFlow(self)
    
    
    
    
    
    
    
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
        hand_index = 0
        while hand_index < len(self.player_hands):
            hand = self.player_hands[hand_index]
            self.current_hand_index = hand_index
            
            if hand.is_blackjack():
                print(f"\nHand {hand_index + 1}: BLACKJACK!")
                hand_index += 1
                continue
            
            first_action = True
            while not hand.is_bust() and not hand.is_surrendered:
                if not first_action:
                    self.show_hands()
                
                if len(self.player_hands) > 1:
                    print(f"\nPlaying Hand {hand_index + 1}")
                
                actions = ['hit', 'stand']
                
                if first_action or len(self.player_hands) == 1:
                    actions.append('surrender')
                
                if hand.can_double and self.player_money >= hand.bet:
                    actions.append('double')
                
                if hand.can_split() and self.player_money >= hand.bet:
                    actions.append('split')
                
                print(f"Actions: {', '.join(actions)}")
                action = input("What would you like to do? ").lower().strip()
                
                if action == 'hit':
                    if self.player_actions.hit(hand):
                        break
                
                elif action == 'stand':
                    break
                
                elif action == 'surrender' and 'surrender' in actions:
                    if self.player_actions.surrender(hand):
                        break
                
                elif action == 'double' and 'double' in actions:
                    if self.player_actions.double_down(hand):
                        break
                
                elif action == 'split' and 'split' in actions:
                    if self.player_actions.split(hand_index):
                        # Continue playing the current hand (don't break)
                        # The split method already dealt one card to each hand
                        first_action = False  # Reset first_action to show hands on next iteration
                
                else:
                    print("Invalid action!")
                
                first_action = False
            
            hand_index += 1
            
            # Show hands when transitioning to next hand (if there is one)
            if hand_index < len(self.player_hands):
                self.current_hand_index = hand_index
                self.show_hands()
    
    
    
    
    def play_round(self):
        if self.player_money <= 0:
            print("You're out of money! Game over.")
            return False
        
        bet = self.game_flow.place_bet()
        self.player_money -= bet
        
        self.game_flow.deal_initial_cards()
        self.player_hands[0].bet = bet
        
        self.show_hands()
        
        insurance_offered = self.game_flow.offer_insurance()
        
        dealer_has_blackjack = self.dealer_actions.check_blackjack()
        
        if insurance_offered:
            self.game_flow.handle_insurance_payout()
        
        if dealer_has_blackjack:
            print(f"\nDealer reveals: {self.dealer_hand}")
            print("Dealer has BLACKJACK!")
            
            if self.player_hands[0].is_blackjack():
                print("Both have BLACKJACK! It's a push!")
                self.player_money += bet  # Return the bet
            else:
                print("You lose!")
                # Bet was already deducted, no additional action needed
        elif self.player_hands[0].is_blackjack():
            print("BLACKJACK! You win!")
            self.player_money += bet + int(bet * 1.5)  # Return bet + winnings
        else:
            self.player_turn()
            
            if not all(hand.is_bust() or hand.is_surrendered for hand in self.player_hands):
                self.dealer_actions.play_turn()
            
            self.game_flow.determine_winner()
        
        return True
    
    def play(self):
        print("Welcome to Blackjack!")
        print("Rules: Get closer to 21 than the dealer without going over.")
        print("Face cards = 10, Aces = 1 or 11, Number cards = face value")
        print("-" * 50)
        
        while True:
            if not self.play_round():
                break
            print("-" * 50)
        
        print(f"Thanks for playing! Final money: ${self.player_money}")

if __name__ == "__main__":
    game = BlackjackGame()
    game.play()