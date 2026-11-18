import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import engine  # noqa: E402

ORDERS = [
    {"customer": "C001", "products": ["Laptop", "Mouse", "Keyboard"]},
    {"customer": "C002", "products": ["Laptop", "Mouse"]},
    {"customer": "C003", "products": ["Laptop", "Keyboard", "Monitor"]},
]


class TestEngine(unittest.TestCase):
    def test_pair_counts(self):
        pairs = engine.count_pairs(ORDERS)
        self.assertEqual(pairs[("Laptop", "Mouse")], 2)
        self.assertEqual(pairs[("Keyboard", "Laptop")], 2)
        self.assertEqual(pairs[("Laptop", "Monitor")], 1)

    def test_repeated_product_counted_once(self):
        orders = [{"customer": "C1", "products": ["A", "B", "B", "A"]}]
        self.assertEqual(engine.count_pairs(orders)[("A", "B")], 1)

    def test_product_recommendations_ranked(self):
        recs = engine.recommend_for_product(ORDERS, "Laptop")
        self.assertEqual(recs, [("Keyboard", 2), ("Mouse", 2), ("Monitor", 1)])  # tie -> alphabetical

    def test_fewer_than_three(self):
        orders = [{"customer": "C1", "products": ["A", "B"]}]
        self.assertEqual(engine.recommend_for_product(orders, "A"), [("B", 1)])

    def test_unknown_product(self):
        self.assertEqual(engine.recommend_for_product(ORDERS, "Banana"), [])

    def test_customer_excludes_owned(self):
        kind, recs = engine.recommend_for_customer(ORDERS, "C002")  # owns Laptop, Mouse
        self.assertEqual(kind, "personal")
        names = [r[0] for r in recs]
        self.assertNotIn("Laptop", names)
        self.assertNotIn("Mouse", names)
        self.assertEqual(names[0], "Keyboard")  # Laptop+Keyboard 2, Mouse+Keyboard 1 => 3

    def test_new_customer_gets_bestsellers(self):
        kind, recs = engine.recommend_for_customer(ORDERS, "NEW")
        self.assertEqual(kind, "bestseller")
        self.assertEqual(recs[0], ("Laptop", 3))

    def test_customer_owns_everything(self):
        orders = [{"customer": "C1", "products": ["A", "B"]}]
        kind, recs = engine.recommend_for_customer(orders, "C1")
        self.assertEqual(recs, [])

    def test_empty_orders(self):
        self.assertEqual(engine.count_pairs([]), {})
        self.assertEqual(engine.best_sellers([]), [])
        kind, recs = engine.recommend_for_customer([], "C1")
        self.assertEqual(recs, [])

    def test_similar_customer(self):
        self.assertEqual(engine.similar_customer(ORDERS, "C002"), ("C001", 2))
        self.assertIsNone(engine.similar_customer(ORDERS, "NEW"))


if __name__ == "__main__":
    unittest.main()
