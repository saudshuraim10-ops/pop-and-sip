from flask import Flask, request

app = Flask(__name__)

@app.route("/ussd", methods=["POST"])
def ussd():
    text = request.form.get("text", "").strip()

    if text == "":
        response = """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    elif text == "1":
        response = """CON POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""

    elif text == "1*0":
        response = """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    elif text == "2":
        response = """CON HIBISCUS DRINK
1. 1 Bottle
2. 2 Bottles
3. 5 Bottles
0. Back"""

    elif text == "2*0":
        response = """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    elif text == "3":
        response = """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""

    elif text == "3*0":
        response = """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    elif text == "4":
        response = """END POP & SIP
WhatsApp: 0595529279
Thank you for choosing Pop & Sip!"""

    else:
        response = "END Thank you for using Pop & Sip."

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
