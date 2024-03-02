from flask import Flask

app = Flask(__name__)

@app.route("/sample")
def members():
    return {"sample": ["sample1", "sample2", "sample3"]}

if __name__ == "__main__":
    app.run(debug=True)