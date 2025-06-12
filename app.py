from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import google.generativeai as genai
import os

# ========== Gemini API 初始化 ==========
genai.configure(api_key="GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")
# ========== Flask 初始化與 Session 設定 ==========
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "這是預設秘密金鑰")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./session_data"
app.config["SESSION_PERMANENT"] = False
Session(app)

# ========== 角色提示語 ==========
role_A_prompt = "你是一位情緒化又固執的人，針對以下主題強烈發表意見："
role_B_prompt = "你是一位冷靜又強詞奪理的人，針對對方的話進行反駁："

# ========== Gemini 回應函式 ==========
def generate_reply(prompt_prefix, history):
    full_prompt = prompt_prefix + "\n" + "\n".join(history)
    response = model.generate_content(full_prompt)
    return response.text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["topic"] = request.form["topic"]
        session["history"] = [f"主題：{session['topic']}"]
        session["round"] = 0
        return redirect(url_for("fight"))
    return render_template("index.html")

@app.route("/fight", methods=["GET", "POST"])
def fight():
    topic = session.get("topic", "無主題")
    history = session.get("history", [])
    round_num = session.get("round", 0)

    if round_num >= 5:
        return render_template("result.html", history=history, topic=topic)

    if request.method == "POST":
        a_reply = generate_reply(role_A_prompt, history)
        history.append(f"角色A：{a_reply}")

        b_reply = generate_reply(role_B_prompt, history)
        history.append(f"角色B：{b_reply}")

        session["history"] = history[-20:]
        session["round"] = round_num + 1
        return redirect(url_for("fight"))

    return render_template("fight.html", history=history, topic=topic, round=round_num)

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    os.makedirs("./session_data", exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    



