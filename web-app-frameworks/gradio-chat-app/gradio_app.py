import gradio as gr
import websocket
import json

def chatbot_function(message, history):
    # Create a WebSocket connection
    ws = websocket.WebSocket()
    ws.connect('websocket-url')

    # Send the user's message to the WebSocket API
    ws.send(json.dumps({"action": "sendmessage", "message": message}))

    # Receive the response from the WebSocket API
    response = ws.recv()

    image_base64_dict = json.loads(response)
    image_base64 = image_base64_dict["image"]

    # Create an HTML string that includes the base64 image
    img_html = f'<img src="data:image/png;base64,{image_base64}" />'
    response_text = "This is generated plot"

    return response_text + "\n\n" + img_html

iface = gr.ChatInterface(fn=chatbot_function)
iface.launch()