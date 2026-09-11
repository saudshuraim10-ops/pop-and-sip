from flask import Flask, request

app = Flask(__name__)

# --------------------------------------------------
# POP & SIP USSD
# --------------------------------------------------

@app.route("/ussd", methods=["POST"])
def ussd():

    text = request.form.get("text", "").strip()

    # Africa's Talking sends cumulative selections separated by *
    parts = text.split("*") if text else []

    # --------------------------------------------------
    # FIRST SCREEN
    # --------------------------------------------------
    if text == "":
        return """CON POP & SIP
1. Place Order
2. Contact Us"""

    # --------------------------------------------------
    # MAIN MENU
    # --------------------------------------------------
    if parts == ["1"]:
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""

    if parts == ["2"]:
        return """END CONTACT US

WhatsApp: 0595529279"""

    # --------------------------------------------------
    # BACK TO MAIN MENU
    # --------------------------------------------------
    if parts == ["1", "0"]:
        return """CON POP & SIP
1. Place Order
2. Contact Us"""

    # --------------------------------------------------
    # POPCORN MENU
    # --------------------------------------------------
    if parts == ["1", "1"]:
        return """CON SELECT POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""

    # --------------------------------------------------
    # BACK FROM POPCORN MENU
    # --------------------------------------------------
    if parts == ["1", "1", "0"]:
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""

    # --------------------------------------------------
    # POPCORN PRODUCT SELECTED
    # --------------------------------------------------
    if len(parts) == 3 and parts[:2] == ["1", "1"] and parts[2] in ["1", "2", "3"]:

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

        product = product_names[parts[2]]
        price = prices[parts[2]]

        return f"""CON SELECT QUANTITY
1. 1
2. 2
3. 3
4. Choose Quantity
0. Back"""

    # --------------------------------------------------
    # BACK FROM POPCORN QUANTITY
    # --------------------------------------------------
    if len(parts) == 4 and parts[:2] == ["1", "1"] and parts[2] in ["1", "2", "3"] and parts[3] == "0":
        return """CON SELECT POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""

    # --------------------------------------------------
    # POPCORN CUSTOM QUANTITY PROMPT
    # --------------------------------------------------
    if len(parts) == 4 and parts[:2] == ["1", "1"] and parts[2] in ["1", "2", "3"] and parts[3] == "4":
        return """CON CHOOSE QUANTITY
Enter the number of items you want.
Example: 7
0. Back"""

    # --------------------------------------------------
    # POPCORN QUANTITY - PRESET OR CUSTOM
    # --------------------------------------------------
    if len(parts) >= 4 and parts[:2] == ["1", "1"] and parts[2] in ["1", "2", "3"]:

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

        price = prices[product_choice]
        product = product_names[product_choice]

        # Preset quantity
        if parts[3] in ["1", "2", "3"]:
            quantity = int(parts[3])

            total = price * quantity

            return f"""CON CUSTOMER DETAILS
Enter your full name:"""

        # Custom quantity
        if parts[3] == "4":

            # Need the actual quantity
            if len(parts) == 5:

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

            # Customer name after custom quantity
            if len(parts) == 6:

                return """CON CUSTOMER DETAILS
Enter your phone number:"""

            # Phone number after custom quantity
            if len(parts) >= 7:

                return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""


    # --------------------------------------------------
    # POPCORN CUSTOMER DETAILS - PRESET QUANTITY
    # --------------------------------------------------
    if len(parts) == 5 and parts[:2] == ["1", "1"] and parts[2] in ["1", "2", "3"]:

        return """CON CUSTOMER DETAILS
Enter your phone number:"""

    # --------------------------------------------------
    # POPCORN CONFIRMATION - PRESET
    # --------------------------------------------------
    if len(parts) == 6 and parts[:2] == ["1", "1"] and parts[2] in ["1", "2", "3"]:

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""

    # --------------------------------------------------
    # POPCORN FINAL CONFIRMATION
    # --------------------------------------------------
    if len(parts) >= 7 and parts[:2] == ["1", "1"] and parts[2] in ["1", "2", "3"]:

        if parts[-1] == "1":

            return """END ORDER CONFIRMED!

Thank you for ordering from Pop & Sip.

PAYMENT

MTN MoMo: 0533809457
Name: POP AND SIP

Please make payment and keep your
transaction ID.

We will contact you to confirm
your order.

WhatsApp: 0595529279"""

        if parts[-1] == "2":

            return """END ORDER CANCELLED.

Thank you for choosing Pop & Sip."""

    # --------------------------------------------------
    # HIBISCUS DRINK MENU
    # --------------------------------------------------
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
    # BACK FROM HIBISCUS
    # --------------------------------------------------
    if parts == ["1", "2", "0"]:
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""

    # --------------------------------------------------
    # HIBISCUS PRESET QUANTITY
    # --------------------------------------------------
    if len(parts) == 3 and parts[:2] == ["1", "2"] and parts[2] in ["1", "2", "3"]:

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
    # HIBISCUS PRESET NAME -> PHONE
    # --------------------------------------------------
    if len(parts) == 4 and parts[:2] == ["1", "2"] and parts[2] in ["1", "2", "3"]:

        return """CON CUSTOMER DETAILS
Enter your phone number:"""

    # --------------------------------------------------
    # HIBISCUS PRESET CONFIRMATION
    # --------------------------------------------------
    if len(parts) == 5 and parts[:2] == ["1", "2"] and parts[2] in ["1", "2", "3"]:

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""

    # --------------------------------------------------
    # HIBISCUS CUSTOM NAME -> PHONE
    # --------------------------------------------------
    if len(parts) == 5 and parts[:3] == ["1", "2", "4"]:

        return """CON CUSTOMER DETAILS
Enter your phone number:"""

    # --------------------------------------------------
    # HIBISCUS CUSTOM CONFIRMATION
    # --------------------------------------------------
    if len(parts) == 6 and parts[:3] == ["1", "2", "4"]:

        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""

    # --------------------------------------------------
    # HIBISCUS FINAL CONFIRMATION
    # --------------------------------------------------
    if len(parts) >= 6 and parts[:2] == ["1", "2"]:

        if parts[-1] == "1":

            return """END ORDER CONFIRMED!

Thank you for ordering from Pop & Sip.

PAYMENT

MTN MoMo: 0533809457
Name: POP AND SIP

Please make payment and keep your
transaction ID.

We will contact you to confirm
your order.

WhatsApp: 0595529279"""

        if parts[-1] == "2":

            return """END ORDER CANCELLED.

Thank you for choosing Pop & Sip."""

    # --------------------------------------------------
    # INVALID OPTION
    # --------------------------------------------------
    return """END Sorry, something went wrong.

Please dial the Pop & Sip USSD code
again and try again."""


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
