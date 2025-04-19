from flask import Flask, request
from sidecar import Sidecar
import threading
import time
import math

sidecar = Sidecar("coordinator")
app = Flask(__name__)

nodes = {
    "proposers": [],
    "acceptors": [],
    "learner": None
}


@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the Coordinator"}


@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    node_type = data.get("type")
    node_url = data.get("url")

    if not (node_type and node_url):
        return {"error": "Missing url"}, 400

    if node_type == "proposer":
        register_proposer(node_url)
    elif node_type == "acceptor":
        register_acceptor(node_url)
    elif node_type == "learner":
        register_learner(node_url)
    else:
        return {"error": "Invalid node type"}, 400

    assign_ranges()
    broadcast_nodes()
    return {"status": "Registered"}


def register_proposer(node_url):
    if not any(p["url"] == node_url for p in nodes["proposers"]):
        nodes["proposers"].append({"url": node_url, "range": None})
    else:
        print(f"Proposer {node_url} already registered")


def register_acceptor(node_url):
    if not any(a["url"] == node_url for a in nodes["acceptors"]):
        nodes["acceptors"].append({"url": node_url})


def register_learner(node_url):
    nodes["learner"] = {"url": node_url}


@app.route("/start", methods=["POST"])
def start():
    data = request.json or {}
    filename = data.get("filename", "sample.txt")

    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            process_lines(lines)
        return {"status": "Document processed"}
    except Exception as e:
        return {"error": str(e)}, 500


def process_lines(lines):
    for line in lines:
        line = line.strip()
        if line:
            for proposer in nodes["proposers"]:
                sidecar.send(f"{proposer['url']}/line", {"text": line}, retries=3, delay=1)


def assign_ranges():
    num_proposers = len(nodes["proposers"])
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    if num_proposers == 0:
        return

    letters_per_proposer = math.ceil(len(letters) / num_proposers)
    for i, proposer in enumerate(nodes["proposers"]):
        start_idx = i * letters_per_proposer
        end_idx = min(start_idx + letters_per_proposer - 1, len(letters) - 1)
        if start_idx < len(letters):
            letter_range = f"{letters[start_idx]}-{letters[end_idx]}"
            proposer["range"] = letter_range
            sidecar.send(f"{proposer['url']}/set_range", {"range": letter_range}, retries=3, delay=1)
            print(f"Assigned {letter_range} to {proposer['url']}")


def broadcast_nodes():
    node_info = {
        "proposers": nodes["proposers"],
        "acceptors": nodes["acceptors"],
        "learner": nodes["learner"]
    }

    for proposer in nodes["proposers"]:
        sidecar.send(f"{proposer['url']}/nodes", node_info, retries=3, delay=1)
    for acceptor in nodes["acceptors"]:
        sidecar.send(f"{acceptor['url']}/nodes", node_info, retries=3, delay=1)
    if nodes["learner"]:
        sidecar.send(f"{nodes['learner']['url']}/nodes", node_info, retries=3, delay=1)


def run_coordinator():

    print("Coordinator is running on port 5020")

    def send_test_request():
        time.sleep(1)
        sidecar.send("http://127.0.0.1:5020/register",
                     {"type": "proposer", "url": "http://127.0.0.1:5002"},
                     retries=3, delay=1)

    test_thread = threading.Thread(target=send_test_request)
    test_thread.daemon = True
    test_thread.start()

    app.run(host="127.0.0.1", port=5020)


if __name__ == "__main__":
    run_coordinator()