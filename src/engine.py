"""BuyNext engine: orders, co-purchase counts and recommendations.

Only uses the Python standard library (dicts, sets, lists, sorting).
"""

import json
from collections import Counter


# ---------------------------------------------------------------- orders

def load_orders(path):
    """Read orders from a JSON file. Returns [] if the file does not exist."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_orders(orders, path):
    """Write orders to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)


def add_order(orders, customer, products):
    """Add one order (customer id + list of products) to the list."""
    orders.append({"customer": customer, "products": list(products)})


def unique_products(order):
    """Products in one order, each counted once (repeats removed, blanks ignored)."""
    return {p.strip() for p in order["products"] if p.strip()}


# ---------------------------------------------------------- co-purchases

def count_pairs(orders):
    """Count how many orders contain each unordered pair of products.

    Returns {(product_a, product_b): number_of_orders} with product_a < product_b.
    A pair is counted once per order, even if a product is repeated in it.
    """
    pairs = Counter()
    for order in orders:
        items = sorted(unique_products(order))
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                pairs[(items[i], items[j])] += 1
    return pairs


def co_counts(orders):
    """Return {product: Counter({other_product: orders_together})}."""
    table = {}
    for (a, b), n in count_pairs(orders).items():
        table.setdefault(a, Counter())[b] = n
        table.setdefault(b, Counter())[a] = n
    return table


def best_sellers(orders):
    """Products ranked by number of orders they appear in."""
    counts = Counter()
    for order in orders:
        for product in unique_products(order):
            counts[product] += 1
    return rank(counts)


def rank(counter):
    """Sort (item, score) high to low; ties are broken alphabetically."""
    return sorted(counter.items(), key=lambda x: (-x[1], x[0]))


# --------------------------------------------------------- recommendations

def recommend_for_product(orders, product, n=3):
    """Top-n products bought most often with `product`.

    Returns a list of (other_product, orders_together). Empty if unknown product.
    """
    others = co_counts(orders).get(product, Counter())
    return rank(others)[:n]


def customer_history(orders, customer):
    """Set of all products a customer has bought."""
    bought = set()
    for order in orders:
        if order["customer"] == customer:
            bought |= unique_products(order)
    return bought


def recommend_for_customer(orders, customer, n=3):
    """Recommend n products the customer has not bought.

    Returns (kind, results):
      kind "personal"   -> results are (product, score, reasons), where reasons is
                           a list of (product_they_bought, orders_together)
      kind "bestseller" -> results are (product, orders_containing_it)
    A customer with no history gets best-sellers. If personal recommendations
    run out before n, the rest are filled from best-sellers.
    """
    history = customer_history(orders, customer)
    if not history:
        return "bestseller", best_sellers(orders)[:n]

    table = co_counts(orders)
    scores = Counter()
    reasons = {}
    for owned in history:
        for other, count in table.get(owned, {}).items():
            if other in history:
                continue
            scores[other] += count
            reasons.setdefault(other, []).append((owned, count))

    results = [(p, s, reasons[p]) for p, s in rank(scores)[:n]]

    # Not enough personal picks? Top up with best-sellers they don't own.
    if len(results) < n:
        have = {p for p, _, _ in results}
        for product, count in best_sellers(orders):
            if len(results) == n:
                break
            if product not in history and product not in have:
                results.append((product, 0, [("(best-seller)", count)]))
    return "personal", results


def similar_customer(orders, customer):
    """Customer sharing the most purchases with `customer`.

    Returns (other_customer, shared_products_count) or None.
    """
    mine = customer_history(orders, customer)
    best = None
    for other in sorted({o["customer"] for o in orders}):
        if other == customer:
            continue
        shared = len(mine & customer_history(orders, other))
        if shared > 0 and (best is None or shared > best[1]):
            best = (other, shared)
    return best
