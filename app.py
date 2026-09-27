from flask import Flask, render_template, request, Response
from dotenv import load_dotenv
import os
from volcenginesdkarkruntime import Ark

load_dotenv()
app = Flask(__name__)

api_key = os.getenv("ARK_API_KEY")
endpoint_id = os.getenv("MODEL_EP_ID")
print("api_key:", api_key)
print("endpoint_id:", endpoint_id)

client = Ark(
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    if not user_msg:
        return "empty message",400

    def stream():
        try:
            resp = client.chat.completions.create(
                model=endpoint_id,
                messages=[
                    {"role":"system","content":"你是一个友好的AI助手"},
                    {"role":"user","content":user_msg}
                ],
                stream=True
            )
            for chunk in resp:
                if chunk.choices and len(chunk.choices)>0:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        except Exception as e:
            print("API调用异常：", e)
            yield f"\n【错误】{str(e)}"
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
