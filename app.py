from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/rc", methods=["GET"])
def get_rc_details():
    first = request.args.get("first")
    second = request.args.get("second")
    if not first or not second:
        return jsonify({"error": "Provide both first and second parameters"}), 400

    session = requests.Session()

    # Initial GET to fetch token and cookies
    url = "https://parivahan.gov.in/rcdlstatus/"
    res = session.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    token = soup.find("input", {"name": "javax.faces.ViewState"})["value"]

    # Form data
    data = {
        'javax.faces.partial.ajax':'true',
        'javax.faces.source': 'form_rcdl:j_idt32',
        'javax.faces.partial.execute':'@all',
        'javax.faces.partial.render': 'form_rcdl:pnl_show form_rcdl:pg_show form_rcdl:rcdl_pnl',
        'form_rcdl:j_idt32':'form_rcdl:j_idt32',
        'form_rcdl':'form_rcdl',
        'form_rcdl:tf_reg_no1': first,
        'form_rcdl:tf_reg_no2': second,
        'javax.faces.ViewState': token
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    post_res = session.post(url, data=data, headers=headers)
    post_soup = BeautifulSoup(post_res.text, "html.parser")

    response = {}
    for td in post_soup.find_all("td"):
        child = td.find()
        if child and "font-bold" in child.get("class", []):
            key = child.text.strip()
            next_td = td.find_next_sibling("td")
            value = next_td.text.strip() if next_td else ""
            response[key] = value

    return jsonify(response)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
