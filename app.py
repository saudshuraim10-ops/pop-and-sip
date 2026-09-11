from flask import Flask, request, Response
import os
import psycopg2
from datetime import datetime

app = Flask(__name__)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def get_db():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")

    return psycopg2.connect(DATABASE_URL)


def setup_database():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_number VARCHAR(30) UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# --------------------------------------------------
# SAVE ORDER
# --------------------------------------------------

def save_order(customer_name, phone, product, quantity, total):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders
        (order_number, customer_name, phone, product, quantity, total)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        "TEMP",
        customer_name,
        phone,
        product,
        quantity,
        total
    ))

    order_id = cur.fetchone()[0]

    order_number = f"PS-{order_id:05d}"

    cur.execute("""
        UPDATE orders
        SET order_number = %s
        WHERE id = %s
    """, (order_number, order_id))

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

    # Popcorn menu
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
    # POPCORN PRODUCT SELECTED
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
    # POPCORN CUSTOMER NAME
    # --------------------------------------------------

    if len(parts) == 5 and parts[:2] == ["1", "1"]:

        product_choice = parts[2]

        if product_choice not in ["1", "2", "3"]:
            return """END Invalid popcorn selection."""

        # Preset quantity
        if parts[3] in ["1", "2", "3"]:
            return """CON CUSTOMER DETAILS
Enter your full name:"""

        # Custom quantity
        if parts[3] == "4":
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
    # POPCORN PHONE
    # --------------------------------------------------

    if len(parts) == 6 and parts[:2] == ["1", "1"]:

        return """CON CUSTOMER DETAILS
Enter your phone number:"""

    # --------------------------------------------------
    # POPCORN CONFIRMATION
    # --------------------------------------------------

    if len(parts) == 7 and parts[:2] == ["1", "1"]:

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""

    # --------------------------------------------------
    # POPCORN FINAL
    # --------------------------------------------------

    if len(parts) >= 8 and parts[:2] == ["1", "1"]:

        confirmation = parts[-1]

        if confirmation == "2":
            return """END ORDER CANCELLED.

Thank you for choosing Pop & Sip."""

        if confirmation == "1":

            product_choice = parts[2]

            prices = {
                "1": 5,
                "2": 10,
                "3": 25
            }

            product_names = {
                "1": "Plain Popcorn",
                "2": "Flavoured Popcorn",
                "3": "Assorted Popcorn"
            }

            if product_choice not in prices:
                return """END Invalid order."""

            price = prices[product_choice]
            product = product_names[product_choice]

            # Preset quantity
            if parts[3] in ["1", "2", "3"]:
                quantity = int(parts[3])
                name = parts[4]
                phone = parts[5]

            # Custom quantity
            elif parts[3] == "4":
                try:
                    quantity = int(parts[4])
                except ValueError:
                    return """END Invalid quantity."""

                name = parts[5]
                phone = parts[6]

            else:
                return """END Invalid order."""

            total = price * quantity

            try:
                order_number = save_order(
                    name,
                    phone,
                    product,
                    quantity,
                    total
                )
            except Exception as e:
                print("DATABASE ERROR:", e)

                return """END Sorry, your order could not be saved.

Please try again."""

            return f"""END ORDER CONFIRMED!

Order No: {order_number}

Thank you for ordering from Pop & Sip.

Product: {product}
Quantity: {quantity}
Total: GH¢{total}

PAYMENT

MTN MoMo: 0533809457
Name: POP AND SIP

Please make payment and keep your
transaction ID.

We will contact you to confirm
your order.

WhatsApp: 0595529279"""

    # ==================================================
    # HIBISCUS
    # ==================================================

    # Hibiscus menu
    if parts == ["1", "2"]:
        return """CON HIBISCUS DRINK
GH¢5 per bottle

SELECT QUANTITY
1. 1 Bottle
2. 2 Bottles
3. 3 Bottles
4. Choose Quantity
0. Back"""

    # Back from hibiscus
    if parts == ["1", "2", "0"]:
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""

    # --------------------------------------------------
    # HIBISCUS PRESET
    # --------------------------------------------------

    if (
        len(parts) == 3
        and parts[:2] == ["1", "2"]
        and parts[2] in ["1", "2", "3"]
    ):
        return """CON CUSTOMER DETAILS
Enter your full name:"""

    # --------------------------------------------------
    # HIBISCUS CUSTOM
    # --------------------------------------------------

    if parts == ["1", "2", "4"]:
        return """CON CHOOSE QUANTITY
Enter the number of bottles you want.
Example: 7
0. Back"""

    # --------------------------------------------------
    # HIBISCUS CUSTOM QUANTITY
    # --------------------------------------------------

    if len(parts) == 4 and parts[:3] == ["1", "2", "4"]:

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
    # HIBISCUS PHONE
    # --------------------------------------------------

    if (
        len(parts) == 4
        and parts[:2] == ["1", "2"]
        and parts[2] in ["1", "2", "3"]
    ):
        return """CON CUSTOMER DETAILS
Enter your phone number:"""

    # Custom quantity -> phone
    if len(parts) == 5 and parts[:3] == ["1", "2", "4"]:
        return """CON CUSTOMER DETAILS
Enter your phone number:"""

    # --------------------------------------------------
    # HIBISCUS CONFIRMATION
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

    if len(parts) == 6 and parts[:3] == ["1", "2", "4"]:
        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""

    # --------------------------------------------------
    # HIBISCUS FINAL
    # --------------------------------------------------

    if len(parts) >= 6 and parts[:2] == ["1", "2"]:

        confirmation = parts[-1]

        if confirmation == "2":
            return """END ORDER CANCELLED.

Thank you for choosing Pop & Sip."""

        if confirmation == "1":

            # Preset quantity
            if parts[2] in ["1", "2", "3"]:

                quantity = int(parts[2])

                # parts:
                # 1, 2, quantity, name, phone, confirmation

                name = parts[3]
                phone = parts[4]

            # Custom quantity
            elif parts[2] == "4":

                try:
                    quantity = int(parts[3])
                except ValueError:
                    return """END Invalid quantity."""

                # parts:
                # 1, 2, 4, quantity, name, phone, confirmation

                name = parts[4]
                phone = parts[5]

            else:
                return """END Invalid order."""

            product = "Hibiscus Drink"
            total = quantity * 5

            try:
                order_number = save_order(
                    name,
                    phone,
                    product,
                    quantity,
                    total
                )
            except Exception as e:
                print("DATABASE ERROR:", e)

                return """END Sorry, your order could not be saved.

Please try again."""

            return f"""END ORDER CONFIRMED!

Order No: {order_number}

Thank you for ordering from Pop & Sip.

Product: {product}
Quantity: {quantity}
Total: GH¢{total}

PAYMENT

MTN MoMo: 0533809457
Name: POP AND SIP

Please make payment and keep your
transaction ID.

We will contact you to confirm
your order.

WhatsApp: 0595529279"""

    # --------------------------------------------------
    # INVALID
    # --------------------------------------------------

    return """END Sorry, something went wrong.

Please dial the Pop & Sip USSD code
again and try again."""


# ==================================================
# ORDER DASHBOARD
# ==================================================

@app.route("/orders", methods=["GET"])
def orders():

    # Password protection
    password = request.args.get("password", "")

    if not ADMIN_PASSWORD:
        return "ADMIN_PASSWORD has not been configured on Render.", 500

    if password != ADMIN_PASSWORD:
        return """
        <h2>Pop & Sip Orders</h2>
        <form method="get">
            <p>Enter admin password:</p>
            <input type="password" name="password">
            <button type="submit">View Orders</button>
        </form>
        """

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            order_number,
            customer_name,
            phone,
            product,
            quantity,
            total,
            created_at
        FROM orders
        ORDER BY created_at DESC
    """)

    orders_data = cur.fetchall()

    cur.close()
    conn.close()

    rows = ""

    for order in orders_data:

        order_number = order[0]
        name = order[1]
        phone = order[2]
        product = order[3]
        quantity = order[4]
        total = order[5]
        created_at = order[6]

        rows += f"""
        <tr>
            <td>{order_number}</td>
            <td>{name}</td>
            <td>{phone}</td>
            <td>{product}</td>
            <td>{quantity}</td>
            <td>GH¢{total}</td>
            <td>{created_at}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pop & Sip Orders</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <style>

            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}

            h1 {{
                text-align: center;
            }}

            .table-container {{
                overflow-x: auto;
                background: white;
                padding: 10px;
                border-radius: 10px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 850px;
            }}

            th, td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #111;
                color: white;
            }}

            tr:hover {{
                background: #f1f1f1;
            }}

        </style>
    </head>

    <body>

        <h1>POP & SIP ORDERS</h1>

        <div class="table-container">

            <table>

                <tr>
                    <th>Order</th>
                    <th>Customer</th>
                    <th>Phone</th>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Total</th>
                    <th>Date / Time</th>
                </tr>

                {rows}

            </table>

        </div>

    </body>
    </html>
    """

    return Response(html, mimetype="text/html")


# ==================================================
# START SERVER
# ==================================================

if __name__ == "__main__":

    try:
        setup_database()
        print("Database ready.")
    except Exception as e:
        print("DATABASE SETUP ERROR:", e)

    app.run(
        host="0.0.0.0",
        port=10000
    )
