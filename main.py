from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo

from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[],
  response_format={
    "type": "text"
  },
  temperature=1,
  max_completion_tokens=2048,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

app = Flask(__name__)

# MongoDB connection configuration
app.config["MONGO_URI"] = "mongodb+srv://yashb:Yashbalar423324@stockc.bnjpn.mongodb.net/chatgpt"
mongo = PyMongo(app)

@app.route("/")
def home():
    """
    Home route that fetches chat data from MongoDB and renders the index.html template.
    """
    try:
        # Fetch chats from the database
        chats = mongo.db.chats.find({})
        myChats = [chat for chat in chats]
        print(myChats) # Log fetched chats for debugging
        return render_template("index.html", chats=myChats)
    except Exception as e:
        print(f"Error fetching chats: {e}")
        return render_template("index.html", myChats=[])

@app.route("/api", methods=["GET", "POST"])
def qa():
    """
    API route to handle question and answer functionality.
    """
    if request.method == "POST":
        try:
            # Get the question from the request body
            print(request.json)
            question = request.json.get("question")
            if not question:
                return jsonify({"error": "Question is required"}), 400

            # Query MongoDB for the answer
            chat = mongo.db.chats.find_one({"Question": question})
            print(chat)  # Log the chat for debugging

            if chat:
                data = {"result": chat["Answer"]}  # Use correct key names
                return jsonify(data)
            else:
                # Default response if question is not found
               data = {"result": f"Answer of {question}"}
               mongo.db.chats.insert_one({"question": question, "answer": f"Answer from openai for {question}"})
               return jsonify(data)
        except Exception as e:
            print(f"Error in /api POST: {e}")
            return jsonify({"error": "Something went wrong"}), 500

    # Default response for GET requests
    data = {
        "result": "I'm an AI assistant here to help you with various tasks, answer questions, and assist with anything you're working on. If you need assistance with coding, technical topics, or even creative projects, feel free to ask!"
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

