'''Test to ensure rounds are scored properly'''
from unittest import TestCase

from hundredandten.bid import Bid
from hundredandten.constants import BidAmount, RoundStatus
from tests import arrange

# tests in this file run off of seeded games to avoid setting up everything necessary for the tests
# seeds and their expected values in different situations are recorded here
BIDDER_GOES_BACK_SEED = 'a2f28d61-10b9-43db-af47-bce72f5f6edd'
TWO_FIFTEENS_SEED = '6475210b-f627-48de-9347-cfa4485d45fc'
SHOOT_THE_MOON_SEED = '1f209d4c-2d3e-44ad-b49d-9923c7202fbf'

SEEDS_TO_SCORES = {
    BIDDER_GOES_BACK_SEED: {
        BidAmount.FIFTEEN: {'0': 5, '1': -15, '2': 10, '3': 10}},
    TWO_FIFTEENS_SEED: {
        BidAmount.FIFTEEN: {'0': 15, '1': 15, '2': 0, '3': 0},
        BidAmount.TWENTY: {'0': 15, '1': -20, '2': 0, '3': 0},
        BidAmount.SHOOT_THE_MOON: {'0': 15, '1': -60, '2': 0, '3': 0}},
    SHOOT_THE_MOON_SEED: {
        BidAmount.FIFTEEN: {'0': 0, '1': 30, '2': 0, '3': 0},
        BidAmount.SHOOT_THE_MOON: {'0': 0, '1': 60, '2': 0, '3': 0}}}


class TestRoundScoring(TestCase):
    '''Unit tests for scoring a round'''

    def test_bidder_goes_back(self):
        '''Score a round where the bidder bids fifteen and loses the points'''
        seed = BIDDER_GOES_BACK_SEED
        game = arrange.game(RoundStatus.TRICKS, arrange.play_round, seed=seed)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(-15, old_round.scores[old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_share_fifteen(self):
        '''Score a round where the bidder and one other player wins fifteen'''
        seed = TWO_FIFTEENS_SEED
        game = arrange.game(RoundStatus.TRICKS, arrange.play_round, seed=seed)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(15, old_round.scores[old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_lose_twenty(self):
        '''Score a round where the bidder bids twenty and loses'''
        seed = TWO_FIFTEENS_SEED
        game = arrange.game(RoundStatus.TRICKS, seed=seed)
        assert game.active_round.active_bidder

        game.active_round.bids.append(
            Bid(identifier=game.active_round.active_bidder.identifier, amount=BidAmount.TWENTY))

        arrange.play_round(game)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(-20, old_round.scores[old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_shoot_the_moon(self):
        '''Score a round where the bidder shoots the moon and wins'''
        seed = SHOOT_THE_MOON_SEED
        game = arrange.game(RoundStatus.TRICKS, seed=seed)
        assert game.active_round.active_bidder

        game.active_round.bids.append(
            Bid(identifier=game.active_round.active_bidder.identifier,
                amount=BidAmount.SHOOT_THE_MOON))

        arrange.play_round(game)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(60, old_round.scores[old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_thirty(self):
        '''Score a round where the bidder wins all tricks without shooting the moon'''
        seed = SHOOT_THE_MOON_SEED
        game = arrange.game(RoundStatus.TRICKS, arrange.play_round, seed=seed)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(30, old_round.scores[old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_lose_shoot_the_moon(self):
        '''Score a round where the bidder shoots the moon and loses'''
        seed = TWO_FIFTEENS_SEED
        game = arrange.game(RoundStatus.TRICKS, seed=seed)
        assert game.active_round.active_bidder

        game.active_round.bids.append(
            Bid(identifier=game.active_round.active_bidder.identifier,
                amount=BidAmount.SHOOT_THE_MOON))

        arrange.play_round(game)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(-60, old_round.scores[old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)
