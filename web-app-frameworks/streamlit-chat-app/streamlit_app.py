import streamlit as st
import websocket
import io
import json
import base64

# App title
st.set_page_config(page_title="💬 SmartAnalytics Chatbot")

# Sidebar title
with st.sidebar:
    st.title('💬 SmartAnalytics Chatbot')
    st.write('This chatbot leverages Websocket API to display images and text as chat response.')

# Store chat generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = []

# Display or clear chat messages
for message, image_data in st.session_state.messages:
    if isinstance(message, dict) and "role" in message:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    if image_data:
        st.image(base64.b64decode(image_data), use_column_width=True)

def clear_chat_history():
    st.session_state.messages = []
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

def websocket_api_response(prompt):
    # Create a WebSocket connection
    ws = websocket.WebSocket()
    ws.connect('websocket-url')

    # Send the user's message to the WebSocket API
    ws.send(json.dumps({"action": "sendmessage"}))

    # Receive the response from the WebSocket API
    response = ws.recv()

    image_base64_dict = json.loads(response)
    image_base64 = image_base64_dict["image"]

    # Convert base64-encoded image to a file-like object
    image_data = io.BytesIO(base64.b64decode(image_base64))
	
	# Display the image in the Streamlit app
    st.image(image_data, use_column_width=True)

    # Convert file-like object to base64-encoded string
    image_base64 = base64.b64encode(image_data.getvalue()).decode()

    # Append the message and image to the chat history
    st.session_state.messages.append(({"role": "assistant", "content": "Response to the user's prompt"}, image_base64))

# User-provided prompt
if prompt := st.chat_input(disabled=False):
    st.session_state.messages.append(({"role": "user", "content": prompt}, None))
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response if the last message is not from the assistant
    if st.session_state.messages[-1][0]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                websocket_api_response(prompt)