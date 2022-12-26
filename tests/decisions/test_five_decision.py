'''Test to determine five stats'''
from unittest import TestCase

from hundredandten.constants import CardNumber, RoundStatus
from hundredandten.deck import Card, Deck
from tests import arrange


class TestFiveDecisions(TestCase):
    '''Unit tests for five stats'''

    def test_has_five_in_tricks(self):
        '''Finds the five stats'''
        count_has_five = 0
        count_no_five = 0
        bidder_has_five = 0

        bidder_no_five_won = 0

        for _ in range(1000):
            game = arrange.game(RoundStatus.TRICKS)

            duplicate_deck = Deck(seed=game.active_round.deck.seed,
                                  pulled=game.active_round.deck.pulled)
            remaining_cards = duplicate_deck.draw(53 - game.active_round.deck.pulled)

            assert game.active_round.trump
            assert game.active_round.active_bidder

            five_of_trump = Card(CardNumber.FIVE, game.active_round.trump)
            bidder_has_five_in_round = five_of_trump in game.active_round.active_bidder.hand
            five_remaining = five_of_trump in remaining_cards
            bidder_has_five += int(bidder_has_five_in_round)
            count_no_five += int(five_remaining)
            count_has_five += int(not five_remaining)

            arrange.play_round(game)

            if not bidder_has_five_in_round:
                last_round_bidder = game.rounds[-2].active_bidder
                assert last_round_bidder
                last_round_bidder_score = sum(
                    s.value for s in game.rounds[-2].scores
                    if s.identifier == last_round_bidder.identifier)
                bidder_no_five_won = int(last_round_bidder_score > 0)

        print('\n')
        print(f'bidder has five {bidder_has_five}')
        print(f'bidder won without five {bidder_no_five_won}')
        print(f'five not in game {count_no_five}')
        print(f'five in game {count_has_five}')

        self.assertEqual(True, True)
