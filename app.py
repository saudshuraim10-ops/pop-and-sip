from flask import Flask, request

app = Flask(__name__)

@app.route("/ussd", methods=["POST"])
def ussd():
    text = request.form.get("text", "")

    if text == "":
        return """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    if text == "1":
        return """CON POPCORN
1. Plain - GH¢5
2. Flavoured - GH¢10
3. Assorted - GH¢25
0. Back"""

    if text == "1*0":
        return """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    if text == "2":
        return """CON HIBISCUS DRINK
1. 1 Bottle
2. 2 Bottles
3. 5 Bottles
0. Back"""

    if text == "2*0":
        return """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    if text == "3":
        return """CON PLACE ORDER
1. Popcorn
2. Hibiscus Drink
0. Back"""

    if text == "3*0":
        return """CON POP & SIP
1. Popcorn
2. Hibiscus Drink
3. Place Order
4. Contact Us"""

    if text == "4":
        return """END POP & SIP
WhatsApp: 0595529279
Thank you for choosing Pop & Sip!"""

    return """END Invalid option.
Please try again."""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
