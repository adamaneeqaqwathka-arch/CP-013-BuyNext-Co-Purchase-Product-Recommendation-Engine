# BuyNext — "Customers who bought this also bought" (CLI)

A small Python command-line tool that recommends products from past orders.
Standard library only — no installs needed.

## Structure

```text
BuyNext/
├── data/sample_orders.json   # orders (customer + products)
├── src/engine.py             # all the logic
├── tests/test_engine.py      # unit tests
├── main.py                   # the CLI
└── README.md
```

## Usage

```bash
python main.py list                      # show all orders
python main.py pairs                     # co-purchase counts for every pair
python main.py product Laptop            # top 3 bought with Laptop (+ reason)
python main.py customer C001             # top 3 new products for a customer
python main.py customer NEWGUY           # no history -> best-sellers
python main.py bestsellers               # top 3 by number of orders
python main.py similar C001              # most similar customer (stretch)
python main.py add C010 Laptop Mouse     # add an order (saved to the JSON file)
```

Use quotes for names with spaces: `python main.py product "Phone Case"`.

## How it works

1. **Orders** are dicts: `{"customer": "C001", "products": [...]}`.
2. **Co-purchase counting:** for each order, take the unique products and count every pair once.
3. **Product recommendations:** rank other products by how many orders they share with the chosen one.
4. **Customer recommendations:** add up the co-purchase counts for everything the customer bought,
   skip what they already own, rank by total score.
   If fewer than 3 remain, the list is topped up with best-sellers they don't own.
5. **Best-seller fallback:** customers with no history get products ranked by number of orders containing them.
6. **Ties** are broken alphabetically so output is always the same.
7. **Stretch features:** reasons shown with every recommendation; `similar` finds the customer sharing the most purchases.

## Tests

```bash
python -m unittest discover tests
```
