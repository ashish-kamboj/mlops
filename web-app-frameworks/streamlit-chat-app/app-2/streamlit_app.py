import plotly.graph_objects as go
import websockets.client
import streamlit as st
import asyncio
import json

def st_page_display():
    with st.sidebar:
        st.title('💬 SmartAnalytics Chatbot')
        st.write('This chatbot leverages Websocket API to display images and text as chat response.')

    with st.sidebar.form(key='my_form', clear_on_submit=True):
            text_input = st.text_area(label='Enter your query')
            submit_button = st.form_submit_button(label='Submit')

    return text_input, submit_button

async def receive_responses(websocket):
    capturing_responses_status = []
    while True:
        try:
            if(not capturing_responses_status):
                with st.spinner('Generating SQL...'):
                    response = await websocket.recv()  # Wait for a response
                    res = json.loads(response)

                    st.text_area(label="**SQL Query**", key="sql", value=res["sql"])
                    st.markdown('<hr class="css-1l02zno">', unsafe_allow_html=True)
                    capturing_responses_status.append("sql")

            elif("plot" not in capturing_responses_status):
                with st.spinner('Generating Plot...'):
                    response = await websocket.recv()  # Wait for a response
                    res = json.loads(response)

                    figure = go.Figure(json.loads(res["plot"]))
                    st.plotly_chart(figure)
                    st.markdown('<hr class="css-1l02zno">', unsafe_allow_html=True)
                    capturing_responses_status.append("plot")

            elif("summary" not in capturing_responses_status):
                with st.spinner('Generating Summary ...'):
                    response = await websocket.recv()  # Wait for a response
                    res = json.loads(response)

                    st.text_area(label="**Summary**", key="summary", value=res["summary"])
                    capturing_responses_status.append("summary")
        except asyncio.TimeoutError:
            print("Timed out waiting for response.")
        except websockets.WebSocketException as e:
            print(f"WebSocket error: {e}")
            break  # Exit on error

async def main():
    text_input, submit_button = st_page_display()

    if submit_button:
        st.sidebar.write(f'**The text you entered is:**  \n{text_input}')
        st.empty()

        # API details (URL)
        api_url = "websocket-url"

        # Connect to the WebSocket API
        async with websockets.connect(api_url) as websocket:    
            # Send the input data in JSON format
            input_data = {"action": "sendmessage", "input_message": text_input}
            await websocket.send(json.dumps(input_data))

            # Receive and display responses continuously
            await receive_responses(websocket)

if __name__ == "__main__":
    asyncio.run(main())
