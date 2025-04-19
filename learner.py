from flask import Flask, request
from sidecar import Sidecar
import threading
import time


sidecar = Sidecar("learner")
app = Flask(__name__)

results = {}


@app.route("/learn", methods=["POST"])
def learn():

    data = request.json or {}
    letter_range = data.get("letter_range")
    count = data.get("count", 0)
    words = data.get("words", [])

    print(f"Learning: {letter_range} -> count={count}, words={words}")

    if letter_range and words:
        update_results(words)

    return {"status": "Learned"}


def update_results(words):
    for word in words:
        if word:
            start_letter = word[0].lower()
            if start_letter not in results:
                results[start_letter] = {"count": 0, "words": []}
            if word not in results[start_letter]["words"]:
                results[start_letter]["count"] += 1
                results[start_letter]["words"].append(word)


@app.route("/results", methods=["GET"])
def get_results():
    table = [
        {
            "Starting letter": start_letter.upper(),
            "Count": data["count"],
            "Words": ", ".join(data["words"]) if data["words"] else ""
        } for start_letter, data in sorted(results.items())
    ]

    print(f"Returning results: {table}")
    return {"results": table}


@app.route("/reset", methods=["POST"])
def reset():
    global results
    results.clear()
    print("Cleared learner results")
    return {"status": "Results cleared"}


@app.route("/nodes", methods=["POST"])
def update_nodes():
    return {"status": "Nodes updated"}


def run_learner():
    print("Learner is running on port 5004")

    def send_test_request():
        time.sleep(1)
        sidecar.send("http://127.0.0.1:5020/register",
                     {"type": "learner", "url": "http://127.0.0.1:5004"},
                     retries=3, delay=1)

    test_thread = threading.Thread(target=send_test_request)
    test_thread.daemon = True
    test_thread.start()

    app.run(host="127.0.0.1", port=5004)


if __name__ == "__main__":
    run_learner()