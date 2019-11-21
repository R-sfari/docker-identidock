from flask import Flask, request, Response, url_for
import requests
import hashlib
import redis

app = Flask(__name__)

cache = redis.StrictRedis(host='redis', port='6379', db=0)
default_name = "Rami sfari"
salt = "UNIQUE_SALT"


@app.route("/", methods=['GET', 'POST'])
def index():
    
    name = default_name
    if request.method == 'POST':
        name = request.form['name']

    salted_name = salt + name
    name_hash = hashlib.sha256(salted_name.encode()).hexdigest()
    
    header = """
    <html>
        <head>
            <title>Identidock</title>
        </head>
    """

    body = """
    <body>
        <form method="POST">
            <label>Hello</label><input type="text" name="name" value="{}">
            <input type="submit" value="submit">
        </form>
        <p> You look like this man :
        <img src="{}" />
    """.format(name, url_for(".get_identicon", name=name_hash))

    footer = """</body></html>"""

    return header + body + footer


@app.route("/monster/<name>")
def get_identicon(name):

    image = cache.get(name)
    
    if image is None:
        print("cache miss", flush=True)
        r = requests.get("http://dnmonster:8080/monster/" + name + "?size=80")
        image = r.content
        cache.set(name, image)

    return Response(image, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
