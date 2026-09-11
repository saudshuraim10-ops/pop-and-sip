from flask import Flask, request
app = Flask(__name__)
# -------------------------
# PRODUCTS
# -------------------------
POPCORN = {
    "1": ("Plain Popcorn", 5),
    "2": ("Flavoured Popcorn", 10),
    "3": ("Assorted Popcorn", 25)
}
HIBISCUS_PRICE = 5
@app.route("/ussd", methods=["POST"])
def ussd():
    text = request.form.get("text", "").strip()
    parts = text.split("*") if text else []
    # -------------------------
    # MAIN MENU
    # -------------------------
    if text == "":
        return """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""
    # -------------------------
    # POPCORN INFORMATION
    # -------------------------
    elif text == "1":
        return """CON POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""
    # -------------------------
    # HIBISCUS INFORMATION
    # -------------------------
    elif text == "2":
        return """CON HIBISCUS DRINK
GH¢5 per bottle
1. 1 Bottle
2. 2 Bottles
3. 3 Bottles
4. Choose Quantity
0. Back"""
    # -------------------------
    # PLACE ORDER
    # -------------------------
    elif text == "3":
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""
    # -------------------------
    # CONTACT
    # -------------------------
    elif text == "4":
        return """END POP & SIP
WhatsApp: 0595529279
Thank you for choosing Pop & Sip!"""
    # -------------------------
    # BACK
    # -------------------------
    elif text in ["1*0", "2*0", "3*0"]:
        return """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""
    # =====================================================
    # POPCORN ORDER
    # =====================================================
    # Choose popcorn
    elif text == "3*1":
        return """CON SELECT POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""
    # Popcorn product selected
    elif len(parts) == 3 and parts[0:2] == ["3", "1"]:
        product = POPCORN.get(parts[2])
        if product:
            name, price = product
            return f"""CON {name}
Price: GH¢{price} each
SELECT QUANTITY
1. 1
2. 2
3. 3
4. Choose Quantity
0. Back"""
        return """END Invalid selection.
Please try again."""
    # Popcorn preset quantity
    elif (
        len(parts) == 4
        and parts[0:2] == ["3", "1"]
        and parts[2] in ["1", "2", "3"]
        and parts[3] in ["1", "2", "3"]
    ):
        return """CON CUSTOMER DETAILS
Enter your full name:
0. Back"""
    # Popcorn custom quantity
    elif (
        len(parts) == 4
        and parts[0:2] == ["3", "1"]
        and parts[3] == "4"
    ):
        return """CON CHOOSE QUANTITY
Enter the number of items you want.
Example: 7
0. Back"""
    # Popcorn custom quantity entered
    elif (
        len(parts) == 5
        and parts[0:2] == ["3", "1"]
        and parts[3] == "4"
    ):
        try:
            quantity = int(parts[4])
            if quantity <= 0:
                raise ValueError
            return """CON CUSTOMER DETAILS
Enter your full name:
0. Back"""
        except ValueError:
            return """CON INVALID QUANTITY
Please enter a number greater than 0.
Try again:"""
    # =====================================================
    # HIBISCUS ORDER
    # =====================================================
    # Choose hibiscus quantity
    elif text == "3*2":
        return """CON HIBISCUS DRINK
GH¢5 per bottle
SELECT QUANTITY
1. 1 Bottle
2. 2 Bottles
3. 3 Bottles
4. Choose Quantity
0. Back"""
    # Hibiscus preset quantity
    elif (
        len(parts) == 3
        and parts[0:2] == ["3", "2"]
        and parts[2] in ["1", "2", "3"]
    ):
        quantity = int(parts[2])
        total = quantity * HIBISCUS_PRICE
        return f"""CON HIBISCUS DRINK
Quantity: {quantity} bottle(s)
Total: GH¢{total}
Enter your full name:
0. Back"""
    # Hibiscus custom quantity
    elif (
        len(parts) == 3
        and parts[0:2] == ["3", "2"]
        and parts[2] == "4"
    ):
        return """CON CHOOSE QUANTITY
Enter the number of bottles you want.
Example: 7
0. Back"""
    # Hibiscus custom quantity entered
    elif (
        len(parts) == 4
        and parts[0:2] == ["3", "2"]
        and parts[2] == "4"
    ):
        try:
            quantity = int(parts[3])
            if quantity <= 0:
                raise ValueError
            total = quantity * HIBISCUS_PRICE
            return f"""CON HIBISCUS DRINK
Quantity: {quantity} bottle(s)
Total: GH¢{total}
Enter your full name:
0. Back"""
        except ValueError:
            return """CON INVALID QUANTITY
Please enter a number greater than 0.
Try again:"""
    # =====================================================
    # CUSTOMER DETAILS
    # =====================================================
    # Preset popcorn → name
    elif (
        len(parts) == 5
        and parts[0:2] == ["3", "1"]
        and parts[3] in ["1", "2", "3"]
    ):
        return """CON PHONE NUMBER
Enter your phone number:
0. Back"""
    # Custom popcorn → name
    elif (
        len(parts) == 6
        and parts[0:2] == ["3", "1"]
        and parts[3] == "4"
    ):
        return """CON PHONE NUMBER
Enter your phone number:
0. Back"""
    # Hibiscus preset → phone
    elif (
        len(parts) == 4
        and parts[0:2] == ["3", "2"]
        and parts[2] in ["1", "2", "3"]
    ):
        return """CON PHONE NUMBER
Enter your phone number:
0. Back"""
    # Hibiscus custom → phone
    elif (
        len(parts) == 5
        and parts[0:2] == ["3", "2"]
        and parts[2] == "4"
    ):
        return """CON PHONE NUMBER
Enter your phone number:
0. Back"""
    # =====================================================
    # CONFIRMATION
    # =====================================================
    elif len(parts) >= 6 and parts[0] == "3":
        return """CON CONFIRM ORDER
1. Confirm Order
2. Cancel Order
0. Back"""
    # =====================================================
    # CONFIRM
    # =====================================================
    elif parts[-1] == "1" and parts[0] == "3":
        return """END ORDER RECEIVED!
Thank you for ordering from Pop & Sip.
MTN MoMo: 0533809457
Name: POP AND SIP
Please make payment and keep your transaction ID.
We will contact you to confirm your order."""
    # =====================================================
    # CANCEL
    # =====================================================
    elif parts[-1] == "2" and parts[0] == "3":
        return """END ORDER CANCELLED
Thank you for choosing Pop & Sip."""
    # =====================================================
    # INVALID
    # =====================================================
    return """END Invalid option.
Please try again."""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
