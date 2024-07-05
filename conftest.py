import unittest


class FooTests(unittest.TestCase):

    def test_with_factory_boy(self):
        # We need a 200€, paid order, shipping to australia, for a VIP customer
        order = OrderFactory(
            amount=200,
            status='PAID',
            customer__is_vip=True,
            address__country='AU',
        )