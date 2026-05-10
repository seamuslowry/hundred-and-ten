"""Test behavior of the Game when going around discarding"""

from unittest import TestCase

from hundredandten.engine.actions import Discard
from hundredandten.engine.constants import HAND_SIZE, Status
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.player import player_after
from hundredandten.testing import arrange


class TestDiscard(TestCase):
    """Unit tests for discarding within a round of Game"""

    def test_error_when_not_discarding(self):
        """Can't discard if not in discard status"""

        game = arrange.game(Status.BIDDING)

        self.assertRaises(HundredAndTenError, game.act, Discard("", []))

    def test_cant_discard_when_not_active(self):
        """Can't discard if not the active player"""

        game = arrange.game(Status.DISCARD)
        inactive_player = game.active_round.inactive_players[0]

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Discard(inactive_player.identifier, inactive_player.hand),
        )

    def test_cant_discard_other_players_cards(self):
        """Can't discard cards that aren't your own"""

        game = arrange.game(Status.DISCARD)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Discard(
                game.active_round.active_player.identifier,
                game.active_round.inactive_players[0].hand,
            ),
        )

    def test_discard_whole_hand(self):
        """Can discard your whole hand"""

        game = arrange.game(Status.DISCARD)

        player = game.active_round.active_player
        initial_hand = list(player.hand)
        discard = Discard(player.identifier, player.hand)
        game.act(discard)

        self.assertEqual(HAND_SIZE, len(player.hand))
        self.assertEqual(HAND_SIZE, len(initial_hand))
        self.assertFalse(any(card in player.hand for card in initial_hand))
        self.assertEqual(discard, game.actions[-1])

    def test_discard_part_of_hand(self):
        """Can discard a part of your hand"""

        game = arrange.game(Status.DISCARD)

        player = game.active_round.active_player
        discard = Discard(player.identifier, [player.hand[1], player.hand[3]])

        remaining_in_hand = [player.hand[0], player.hand[2], player.hand[4]]
        game.act(discard)

        self.assertEqual(HAND_SIZE, len(player.hand))
        self.assertTrue(all(card in player.hand for card in remaining_in_hand))
        self.assertFalse(any(card in player.hand for card in discard.cards))
        self.assertEqual(discard, game.actions[-1])

    def test_dealer_is_first_to_discard(self):
        """The dealer is the first active player when DISCARD begins"""

        game = arrange.game(Status.DISCARD)

        self.assertEqual(
            game.active_round.dealer,
            game.active_round.active_player,
        )

    def test_discard_order_is_clockwise_from_dealer(self):
        """Turn order during DISCARD proceeds clockwise from the dealer"""

        game = arrange.game(Status.DISCARD)
        round_ = game.active_round
        dealer = round_.dealer

        # Collect the active player identity before each of the 4 discards
        active_players = []
        for _ in range(len(round_.players)):
            active_players.append(round_.active_player)
            game.act(Discard(round_.active_player.identifier, []))

        # First actor must be the dealer
        self.assertEqual(dealer, active_players[0])

        # Each subsequent actor must be the clockwise successor of the previous
        for i in range(1, len(active_players)):
            self.assertEqual(
                player_after(round_.players, active_players[i - 1].identifier),
                active_players[i],
            )

        # After all four discards the round is in TRICKS
        self.assertEqual(Status.TRICKS, game.status)

    def test_dealer_is_first_to_discard_when_dealer_is_not_first_player(self):
        """The dealer is first to discard even after dealer rotation (round 2+)"""

        # Complete round 1 so the dealer rotates to players[1] for round 2
        game = arrange.game(Status.TRICKS)
        arrange.play_round(game)
        arrange.bid(game)
        arrange.select_trump(game)

        round_ = game.active_round
        dealer = round_.dealer

        # The rotated dealer should not be players[0]
        self.assertNotEqual(dealer, round_.players[0])
        # The active player at the start of DISCARD must still be the dealer
        self.assertEqual(dealer, round_.active_player)
