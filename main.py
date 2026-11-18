"""BuyNext command-line interface.

Examples:
    python main.py list
    python main.py pairs
    python main.py product Laptop
    python main.py customer C001
    python main.py bestsellers
    python main.py similar C001
    python main.py add C010 Laptop Mouse Monitor
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import engine  # noqa: E402

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_orders.json")


def plural(n, word="order"):
    return f"{n} {word}" + ("" if n == 1 else "s")


def cmd_list(orders, args):
    if not orders:
        print("No orders stored.")
    for i, o in enumerate(orders, 1):
        print(f"{i}. {o['customer']}: {', '.join(o['products'])}")


def cmd_pairs(orders, args):
    pairs = engine.count_pairs(orders)
    if not pairs:
        print("No product pairs found.")
        return
    for (a, b), n in engine.rank(pairs):
        print(f"{a} + {b}: {plural(n)}")


def cmd_product(orders, args):
    results = engine.recommend_for_product(orders, args.product)
    if not results:
        print(f"No co-purchase data for '{args.product}' (unknown product or never bought with others).")
        return
    print(f"Customers who bought {args.product} also bought:")
    for i, (product, n) in enumerate(results, 1):
        print(f"{i}. {product}")
        print(f"   Reason: Bought with {args.product} in {plural(n)}.")


def cmd_customer(orders, args):
    kind, results = engine.recommend_for_customer(orders, args.customer)
    if not results:
        print("No recommendations available (no orders stored).")
        return
    if kind == "bestseller":
        print(f"No purchase history for '{args.customer}'. Showing best-sellers:")
        for i, (product, n) in enumerate(results, 1):
            print(f"{i}. {product}  (in {plural(n)})")
        return
    print(f"Recommended for {args.customer}:")
    for i, (product, score, reasons) in enumerate(results, 1):
        print(f"{i}. {product}")
        for owned, n in reasons:
            if owned == "(best-seller)":
                print(f"   Reason: Popular overall, in {plural(n)}.")
            else:
                print(f"   Reason: Bought with {owned} in {plural(n)}.")


def cmd_bestsellers(orders, args):
    top = engine.best_sellers(orders)[:3]
    if not top:
        print("No orders stored.")
        return
    print("Best-sellers:")
    for i, (product, n) in enumerate(top, 1):
        print(f"{i}. {product}  (in {plural(n)})")


def cmd_similar(orders, args):
    result = engine.similar_customer(orders, args.customer)
    if result is None:
        print(f"No similar customer found for '{args.customer}'.")
    else:
        other, shared = result
        print(f"Most similar to {args.customer}: {other} ({shared} shared products)")


def cmd_add(orders, args):
    engine.add_order(orders, args.customer, args.products)
    engine.save_orders(orders, DATA_FILE)
    print(f"Order added for {args.customer}: {', '.join(args.products)}")


def build_parser():
    parser = argparse.ArgumentParser(description="BuyNext - 'Customers who bought this also bought'")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="show all orders").set_defaults(func=cmd_list)
    sub.add_parser("pairs", help="show co-purchase counts").set_defaults(func=cmd_pairs)
    sub.add_parser("bestsellers", help="show top 3 best-selling products").set_defaults(func=cmd_bestsellers)

    p = sub.add_parser("product", help="top 3 products bought with a product")
    p.add_argument("product")
    p.set_defaults(func=cmd_product)

    p = sub.add_parser("customer", help="top 3 recommendations for a customer")
    p.add_argument("customer")
    p.set_defaults(func=cmd_customer)

    p = sub.add_parser("similar", help="find the most similar customer")
    p.add_argument("customer")
    p.set_defaults(func=cmd_similar)

    p = sub.add_parser("add", help="add a new order")
    p.add_argument("customer")
    p.add_argument("products", nargs="+")
    p.set_defaults(func=cmd_add)
    return parser


def main():
    args = build_parser().parse_args()
    orders = engine.load_orders(DATA_FILE)
    args.func(orders, args)


if __name__ == "__main__":
    main()
