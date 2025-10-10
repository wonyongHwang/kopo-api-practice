from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/webhook")
def webhook():
    event = request.headers.get("X-Event-Name", "unknown")
    data = request.get_json(silent=True) or {}
    print(f"[Webhook] event={event} data={data}")
    return jsonify({"received": True, "event": event})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
