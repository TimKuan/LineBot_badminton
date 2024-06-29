from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import util
import reptile
import constant
app = Flask(__name__)

configuration = Configuration(access_token=constant.linebot_token)
handler = WebhookHandler(constant.linebot_secret)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    # 分析使用者傳入的文字訊息，並返回一個用於進一步處理的資料結構
    user_needs = util.analyze_text(event.message.text)
    # 開始進行爬蟲處理
    result = reptile.reptile(user_needs)

    #準備要發送的消息列表
    message = []
    for content in result:
        # 將結果 組成 使用者要看的內容
        analyzed_content = util.analyze_return(content)
        message.append(TextMessage(text=analyzed_content))    
    batch = message[0:5]
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=batch
                )
            )
    except Exception as e:
        print(f"Failed to send messages: {e}")
        


import os
if __name__ == "__main__":
    app.run(port=constant.linebot_port)