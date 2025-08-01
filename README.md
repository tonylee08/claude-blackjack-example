# Blackjack Game

A command-line implementation of the classic Blackjack card game written in Python.

## Features

- **Standard Blackjack Rules**: Get as close to 21 as possible without going over
- **Dealer Hits on Soft 17**: Dealer must hit when holding a soft 17 (e.g., Ace + 2 + 4)
- **Advanced Player Options**:
  - Hit, Stand, Double Down
  - Split pairs
  - Surrender (forfeit half bet)
  - Insurance betting when dealer shows Ace
- **Multiple Hand Support**: Play split hands simultaneously
- **Money Management**: Start with $1000 and track winnings/losses

## How to Play

### Requirements
- Python 3.x

### Running the Game
```bash
python blackjack.py
```

### Game Rules

1. **Objective**: Get a hand value closer to 21 than the dealer without exceeding 21
2. **Card Values**:
   - Number cards (2-10): Face value
   - Face cards (J, Q, K): 10 points
   - Aces: 1 or 11 points (automatically optimized)

3. **Gameplay**:
   - Place your bet at the start of each round
   - Receive 2 cards face up; dealer gets 1 face up, 1 face down
   - Choose your actions based on available options

### Player Actions

- **Hit**: Take another card
- **Stand**: Keep your current hand
- **Double Down**: Double your bet and receive exactly one more card
- **Split**: If you have a pair, split into two separate hands (requires additional bet)
- **Surrender**: Forfeit half your bet and end the hand (first action only)
- **Insurance**: Side bet when dealer shows Ace (pays 2:1 if dealer has blackjack)

### Dealer Rules

- Dealer hits on 16 or lower
- Dealer hits on soft 17 (e.g., Ace + 2 + 4)
- Dealer stands on hard 17 or higher

### Winning Conditions

- **Blackjack**: 21 with first 2 cards (pays 3:2)
- **Win**: Higher value than dealer without busting
- **Push**: Same value as dealer (bet returned)
- **Bust**: Hand value exceeds 21 (automatic loss)

## Code Structure

- `Card`: Represents individual playing cards
- `Deck`: Manages the deck of cards with shuffling and dealing
- `Hand`: Manages card collections and calculates values
- `BlackjackGame`: Main game logic and user interface

## License

This project is open source and available under the Apache-2.0 License.