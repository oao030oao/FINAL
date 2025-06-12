from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# 使用 Render 環境變數（建議這樣做）

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "吵架不能沒有記憶")

role_A_prompt = "你是一位情緒化又固執的人，針對主題請用強烈語氣表達立場："
role_B_prompt = "你是一位冷靜又強詞奪理的人，請針對主題反駁："

def generate_reply(prompt_prefix, history):
    try:
        prompt = prompt_prefix + "\n" + "\n".join(history)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=300
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini 回傳錯誤：{e}")
        return "⚠️ 發言失敗（API 出錯），請稍後再試"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["topic"] = request.form["topic"]
        session["max_rounds"] = int(request.form["max_rounds"])
        session["history"] = [f"主題：{session['topic']}"]
        session["turn"] = "A"
        session["count"] = 0
        return redirect(url_for("fight"))
    return render_template("index.html")

@app.route("/fight", methods=["GET", "POST"])
def fight():
    topic = session.get("topic", "無主題")
    history = session.get("history", [])
    turn = session.get("turn", "A")
    count = session.get("count", 0)
    max_rounds = session.get("max_rounds", 5)

    if request.method == "POST":
        if turn == "A":
            reply = generate_reply(role_A_prompt, history)
            history.append(f"角色A：{reply}")
            session["turn"] = "B"
        else:
            reply = generate_reply(role_B_prompt, history)
            history.append(f"角色B：{reply}")
            session["turn"] = "A"
            session["count"] = count + 1

        session["history"] = history

        if session["count"] >= max_rounds:
            return redirect(url_for("result"))

        return redirect(url_for("fight"))

    return render_template("fight.html", history=history, topic=topic, count=count, max_rounds=max_rounds, turn=turn)

@app.route("/result")
def result():
    return render_template("result.html", topic=session.get("topic", ""), history=session.get("history", []))

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
