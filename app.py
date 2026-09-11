from flask import Flask, request, session, redirect, url_for
import os
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "pop-and-sip-secret")

DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_db():
    return psycopg2.connect(DATABASE_URL)


def create_table():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_number VARCHAR(50) UNIQUE NOT NULL,
            product VARCHAR(100) NOT NULL,
            quantity INTEGER NOT NULL,
            total INTEGER NOT NULL,
            customer_name VARCHAR(150) NOT NULL,
            customer_phone VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def save_order(product, quantity, total, customer_name, customer_phone):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(MAX(id), 0) + 1
        FROM orders
    """)

    next_number = cur.fetchone()[0]
    order_number = f"PS-{next_number:05d}"

    cur.execute("""
        INSERT INTO orders
        (order_number, product, quantity, total, customer_name, customer_phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        order_number,
        product,
        quantity,
        total,
        customer_name,
        customer_phone
    ))

    conn.commit()
    cur.close()
    conn.close()

    return order_number


# --------------------------------------------------
# USSD
# --------------------------------------------------

@app.route("/ussd", methods=["POST"])
def ussd():

    text = request.form.get("text", "").strip()
    session_id = request.form.get("sessionId", "")

    parts = text.split("*") if text else []

    # --------------------------------------------------
    # FIRST SCREEN
    # --------------------------------------------------

    if text == "":
        return """CON POP & SIP
1. Place Order
2. Contact Us"""


    # --------------------------------------------------
    # CONTACT US
    # --------------------------------------------------

    if parts == ["2"]:
        return """END CONTACT US

WhatsApp: 0595529279"""


    # --------------------------------------------------
    # MAIN MENU
    # --------------------------------------------------

    if parts == ["1"]:
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""


    # --------------------------------------------------
    # BACK TO MAIN MENU
    # --------------------------------------------------

    if parts == ["1", "0"]:
        return """CON POP & SIP
1. Place Order
2. Contact Us"""


    # ==================================================
    # POPCORN
    # ==================================================

    if parts == ["1", "1"]:
        return """CON SELECT POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""


    # Back from popcorn
    if parts == ["1", "1", "0"]:
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""


    # --------------------------------------------------
    # POPCORN PRODUCT
    # --------------------------------------------------

    if (
        len(parts) == 3
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
    ):

        return """CON SELECT QUANTITY
1. 1
2. 2
3. 3
4. Choose Quantity
0. Back"""


    # --------------------------------------------------
    # POPCORN QUANTITY BACK
    # --------------------------------------------------

    if (
        len(parts) == 4
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
        and parts[3] == "0"
    ):

        return """CON SELECT POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""


    # --------------------------------------------------
    # POPCORN CUSTOM QUANTITY
    # --------------------------------------------------

    if (
        len(parts) == 4
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
        and parts[3] == "4"
    ):

        return """CON CHOOSE QUANTITY
Enter the number of items you want.
Example: 7
0. Back"""


    # --------------------------------------------------
    # POPCORN CUSTOM QUANTITY ENTERED
    # --------------------------------------------------

    if (
        len(parts) == 5
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
        and parts[3] == "4"
    ):

        try:
            quantity = int(parts[4])

            if quantity <= 0:
                return """CON CHOOSE QUANTITY
Enter a number greater than 0.
Example: 7"""

        except ValueError:
            return """CON CHOOSE QUANTITY
Please enter a valid number.
Example: 7"""

        return """CON CUSTOMER DETAILS
Enter your full name:"""


    # --------------------------------------------------
    # POPCORN CUSTOM NAME
    # --------------------------------------------------

    if (
        len(parts) == 6
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
        and parts[3] == "4"
    ):

        return """CON CUSTOMER DETAILS
Enter your phone number:"""


    # --------------------------------------------------
    # POPCORN CUSTOM PHONE
    # --------------------------------------------------

    if (
        len(parts) == 7
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
        and parts[3] == "4"
    ):

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""


    # --------------------------------------------------
    # POPCORN PRESET QUANTITY
    # --------------------------------------------------

    if (
        len(parts) == 4
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
        and parts[3] in ["1", "2", "3"]
    ):

        return """CON CUSTOMER DETAILS
Enter your full name:"""


    # --------------------------------------------------
    # POPCORN PRESET NAME
    # --------------------------------------------------

    if (
        len(parts) == 5
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
    ):

        return """CON CUSTOMER DETAILS
Enter your phone number:"""


    # --------------------------------------------------
    # POPCORN PRESET PHONE
    # --------------------------------------------------

    if (
        len(parts) == 6
        and parts[:2] == ["1", "1"]
        and parts[2] in ["1", "2", "3"]
    ):

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""


    # --------------------------------------------------
    # POPCORN FINAL CONFIRMATION
    # --------------------------------------------------

    if len(parts) >= 7 and parts[:2] == ["1", "1"]:

        if parts[-1] == "2":
            return """END ORDER CANCELLED.

Thank you for choosing Pop & Sip."""

        if parts[-1] == "1":

            product_choice = parts[2]

            prices = {
                "1": 5,
                "2": 10,
                "3": 25
            }

            names = {
                "1": "Plain Popcorn",
                "2": "Flavoured Popcorn",
                "3": "Assorted Popcorn"
            }

            price = prices[product_choice]
            product = names[product_choice]

            if parts[3] == "4":
                quantity = int(parts[4])
                name_index = 5
                phone_index = 6
            else:
                quantity = int(parts[3])
                name_index = 4
                phone_index = 5

            customer_name = parts[name_index]
            customer_phone = parts[phone_index]

            total = price * quantity

            try:
                order_number = save_order(
                    product,
                    quantity,
                    total,
                    customer_name,
                    customer_phone
                )

                return f"""END ORDER CONFIRMED!

Order: {order_number}
Product: {product}
Quantity: {quantity}
Total: GH¢{total}

Thank you for ordering from Pop & Sip.

PAYMENT

MTN MoMo: 0533809457
Name: POP AND SIP

Please make payment and keep your
transaction ID.

We will contact you to confirm
your order.

WhatsApp: 0595529279"""

            except Exception:
                return """END Your order was received,
but there was a database error.

Please contact Pop & Sip on WhatsApp:
0595529279"""


    # ==================================================
    # HIBISCUS DRINK
    # ==================================================

    if parts == ["1", "2"]:
        return """CON HIBISCUS DRINK
GH¢5 per bottle

SELECT QUANTITY
1. 1 Bottle
2. 2 Bottles
3. 3 Bottles
4. Choose Quantity
0. Back"""


    # --------------------------------------------------
    # HIBISCUS BACK
    # --------------------------------------------------

    if parts == ["1", "2", "0"]:
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""


    # --------------------------------------------------
    # HIBISCUS PRESET QUANTITY
    # --------------------------------------------------

    if (
        len(parts) == 3
        and parts[:2] == ["1", "2"]
        and parts[2] in ["1", "2", "3"]
    ):

        return """CON CUSTOMER DETAILS
Enter your full name:"""


    # --------------------------------------------------
    # HIBISCUS CUSTOM QUANTITY
    # --------------------------------------------------

    if parts == ["1", "2", "4"]:
        return """CON CHOOSE QUANTITY
Enter the number of bottles you want.
Example: 7
0. Back"""


    # --------------------------------------------------
    # HIBISCUS CUSTOM QUANTITY ENTERED
    # --------------------------------------------------

    if (
        len(parts) == 4
        and parts[:3] == ["1", "2", "4"]
    ):

        try:
            quantity = int(parts[3])

            if quantity <= 0:
                return """CON CHOOSE QUANTITY
Enter a number greater than 0.
Example: 7"""

        except ValueError:
            return """CON CHOOSE QUANTITY
Please enter a valid number.
Example: 7"""

        return """CON CUSTOMER DETAILS
Enter your full name:"""


    # --------------------------------------------------
    # HIBISCUS PRESET NAME
    # --------------------------------------------------

    if (
        len(parts) == 4
        and parts[:2] == ["1", "2"]
        and parts[2] in ["1", "2", "3"]
    ):

        return """CON CUSTOMER DETAILS
Enter your phone number:"""


    # --------------------------------------------------
    # HIBISCUS PRESET PHONE
    # --------------------------------------------------

    if (
        len(parts) == 5
        and parts[:2] == ["1", "2"]
        and parts[2] in ["1", "2", "3"]
    ):

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""


    # --------------------------------------------------
    # HIBISCUS CUSTOM NAME
    # --------------------------------------------------

    if (
        len(parts) == 5
        and parts[:3] == ["1", "2", "4"]
    ):

        return """CON CUSTOMER DETAILS
Enter your phone number:"""


    # --------------------------------------------------
    # HIBISCUS CUSTOM PHONE
    # --------------------------------------------------

    if (
        len(parts) == 6
        and parts[:3] == ["1", "2", "4"]
    ):

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""


    # --------------------------------------------------
    # HIBISCUS FINAL CONFIRMATION
    # --------------------------------------------------

    if len(parts) >= 6 and parts[:2] == ["1", "2"]:

        if parts[-1] == "2":
            return """END ORDER CANCELLED.

Thank you for choosing Pop & Sip."""

        if parts[-1] == "1":

            product = "Hibiscus Drink"
            price = 5

            if parts[2] == "4":
                quantity = int(parts[3])
                customer_name = parts[4]
                customer_phone = parts[5]
            else:
                quantity = int(parts[2])
                customer_name = parts[3]
                customer_phone = parts[4]

            total = price * quantity

            try:
                order_number = save_order(
                    product,
                    quantity,
                    total,
                    customer_name,
                    customer_phone
                )

                return f"""END ORDER CONFIRMED!

Order: {order_number}
Product: {product}
Quantity: {quantity}
Total: GH¢{total}

Thank you for ordering from Pop & Sip.

PAYMENT

MTN MoMo: 0533809457
Name: POP AND SIP

Please make payment and keep your
transaction ID.

We will contact you to confirm
your order.

WhatsApp: 0595529279"""

            except Exception:
                return """END Your order was received,
but there was a database error.

Please contact Pop & Sip on WhatsApp:
0595529279"""


    # --------------------------------------------------
    # INVALID OPTION
    # --------------------------------------------------

    return """END Sorry, something went wrong.

Please dial the Pop & Sip USSD code
again and try again."""


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route("/orders")
def orders():

    password = request.args.get("password", "")

    if not ADMIN_PASSWORD or password != ADMIN_PASSWORD:
        return """
        <html>
        <head>
            <title>Pop & Sip Admin</title>
        </head>
        <body>
            <h2>Pop & Sip Admin</h2>
            <form method="get">
                <input type="password"
                       name="password"
                       placeholder="Admin Password"
                       required>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT order_number, product, quantity, total,
               customer_name, customer_phone, created_at
        FROM orders
        ORDER BY created_at DESC
    """)

    orders = cur.fetchall()

    cur.close()
    conn.close()

    html = """
    <html>
    <head>
        <title>Pop & Sip Orders</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background: #f5f5f5;
            }

            h1 {
                text-align: center;
            }

            .order {
                background: white;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .order-number {
                font-size: 20px;
                font-weight: bold;
            }

            .total {
                font-size: 18px;
                font-weight: bold;
            }
        </style>
    </head>

    <body>

    <h1>POP & SIP ORDERS</h1>
    """

    if not orders:
        html += "<p>No orders yet.</p>"

    for order in orders:

        order_number = order[0]
        product = order[1]
        quantity = order[2]
        total = order[3]
        customer_name = order[4]
        customer_phone = order[5]
        created_at = order[6]

        html += f"""
        <div class="order">

            <div class="order-number">
                {order_number}
            </div>

            <p>
                <strong>Product:</strong> {product}<br>
                <strong>Quantity:</strong> {quantity}<br>
                <strong>Customer:</strong> {customer_name}<br>
                <strong>Phone:</strong> {customer_phone}
            </p>

            <div class="total">
                Total: GH¢{total}
            </div>

            <p>
                <strong>Date:</strong> {created_at}
            </p>

        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    try:
        create_table()
        print("Database ready.")
    except Exception as e:
        print("Database error:", e)

    app.run(host="0.0.0.0", port=10000)
