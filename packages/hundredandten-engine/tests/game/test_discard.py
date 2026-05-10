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

    def test_dealer_discards_zero_cards_and_draw_order_advances(self):
        """Dealer discarding zero cards is valid and advances the active player"""

        game = arrange.game(Status.DISCARD)
        round_ = game.active_round
        dealer = round_.dealer

        game.act(Discard(dealer.identifier, []))

        # The active player after the dealer discards is the next clockwise seat
        self.assertEqual(
            player_after(round_.players, dealer.identifier),
            round_.active_player,
        )

    def test_dealer_replacement_cards_drawn_on_discard(self):
        """Dealer receives replacement cards equal to the number discarded"""

        game = arrange.game(Status.DISCARD)
        round_ = game.active_round
        dealer = round_.dealer

        cards_to_discard = [dealer.hand[1], dealer.hand[3]]
        kept = [dealer.hand[0], dealer.hand[2], dealer.hand[4]]
        game.act(Discard(dealer.identifier, cards_to_discard))

        self.assertEqual(HAND_SIZE, len(dealer.hand))
        self.assertTrue(all(card in dealer.hand for card in kept))
        self.assertFalse(any(card in dealer.hand for card in cards_to_discard))

    def test_player_after_dealer_cannot_discard_first(self):
        """The player clockwise of the dealer cannot discard before the dealer"""

        game = arrange.game(Status.DISCARD)
        round_ = game.active_round
        player_after_dealer = player_after(round_.players, round_.dealer.identifier)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Discard(player_after_dealer.identifier, []),
        )
