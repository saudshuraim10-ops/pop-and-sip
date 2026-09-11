from flask import Flask, request

app = Flask(__name__)

POPCORN = {
    "1": ("Plain Popcorn", 5),
    "2": ("Flavoured Popcorn", 10),
    "3": ("Assorted Popcorn", 25)
}

# Hibiscus prices can be updated later
HIBISCUS = {
    "1": ("Hibiscus Drink - 1 Bottle", 0),
    "2": ("Hibiscus Drink - 2 Bottles", 0),
    "3": ("Hibiscus Drink - 3 Bottles", 0)
}


@app.route("/ussd", methods=["POST"])
def ussd():
    text = request.form.get("text", "").strip()
    parts = text.split("*") if text else []

    # MAIN MENU
    if text == "":
        response = """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    # POPCORN INFORMATION
    elif text == "1":
        response = """CON POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""

    # HIBISCUS INFORMATION
    elif text == "2":
        response = """CON HIBISCUS DRINK
1. 1 Bottle
2. 2 Bottles
3. 3 Bottles
4. Choose Quantity
0. Back"""

    # PLACE ORDER
    elif text == "3":
        response = """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""

    # CONTACT
    elif text == "4":
        response = """END POP & SIP

WhatsApp: 0595529279

Thank you for choosing Pop & Sip!"""

    # POPCORN ORDER
    elif text == "3*1":
        response = """CON SELECT POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""

    # HIBISCUS ORDER
    elif text == "3*2":
        response = """CON SELECT HIBISCUS
1. 1 Bottle
2. 2 Bottles
3. 3 Bottles
4. Choose Quantity
0. Back"""

    # SELECT POPCORN PRODUCT
    elif len(parts) == 3 and parts[0:2] == ["3", "1"]:
        product = POPCORN.get(parts[2])

        if product:
            name, price = product
            response = f"""CON {name}
Price: GH¢{price}

SELECT QUANTITY
1. 1
2. 2
3. 3
4. Choose Quantity
0. Back"""
        else:
            response = "END Invalid selection."

    # SELECT HIBISCUS PRODUCT
    elif len(parts) == 3 and parts[0:2] == ["3", "2"]:
        if parts[2] in ["1", "2", "3"]:
            name, price = HIBISCUS[parts[2]]

            response = f"""CON {name}

SELECT QUANTITY
1. 1
2. 2
3. 3
4. Choose Quantity
0. Back"""

        elif parts[2] == "4":
            response = """CON CHOOSE QUANTITY
Enter the number of bottles you want:
0. Back"""

        else:
            response = "END Invalid selection."

    # CUSTOMER ENTERS CUSTOM QUANTITY
    elif len(parts) == 4 and parts[0:3] == ["3", "2", "4"]:
        try:
            quantity = int(parts[3])

            if quantity <= 0:
                raise ValueError

            response = """CON CUSTOMER DETAILS
Enter your full name:
0. Back"""

        except ValueError:
            response = """CON INVALID QUANTITY
Please enter a number greater than 0:"""

    # CUSTOMER NAME
    elif len(parts) == 4 and parts[0] == "3":
        response = """CON CUSTOMER DETAILS
Enter your full name:
0. Back"""

    # PHONE NUMBER
    elif len(parts) == 5 and parts[0] == "3":
        response = """CON PHONE NUMBER
Enter your phone number:
0. Back"""

    # CONFIRM ORDER
    elif len(parts) == 6 and parts[0] == "3":
        response = """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""

    # CONFIRMED
    elif len(parts) == 7 and parts[0] == "3" and parts[6] == "1":
        response = """END ORDER RECEIVED!

Thank you for ordering from Pop & Sip.

MTN MoMo: 0533809457
Name: POP AND SIP

Please make payment and keep your transaction ID.

We will contact you to confirm your order."""

    # CANCELLED
    elif len(parts) == 7 and parts[0] == "3" and parts[6] == "2":
        response = """END ORDER CANCELLED

Thank you for choosing Pop & Sip."""

    else:
        response = """END Invalid option.
Please try again."""

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
