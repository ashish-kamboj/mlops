import React, { useEffect, useState } from 'react';
import './App.css';

const App = () => {
    const [imageSrc, setImageSrc] = useState(null);
    const [message, setMessage] = useState('');
    const [socket, setSocket] = useState(null);
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        // Create WebSocket connection.
        const socket = new WebSocket('websocket-url');
        setSocket(socket);

        // Listen for messages
        socket.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);
            console.log('Message from server ', event.data);
            if (data.image) {
                setImageSrc(`data:image/png;base64,${data.image}`);
            }

            if (data.text) {
                setMessages([...messages, `A. ${data.text}`]);
            }
        });

        // Connection closed
        socket.addEventListener('close', (event) => {
            console.log('Server closed connection ', event);
        });

        return () => {
            socket.close();
        };
    }, []);

    const sendMessage = () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({"action": "sendmessage", "data": message}));
            setMessages([...messages, message]);
            setMessage('');
        }
    };

    const handleKeyPress = (event) => {
        if(event.key === 'Enter'){
            sendMessage();
        }
    }

    return (
        <div className="app">
            <div className="sidebar">
                Sidebar content goes here
            </div>
            <div className="main">
                <div className="display-area">
                    {messages.map((message, index) => (
                        <p key={index}><b>Q. {message}</b></p>
                    ))}
                    {imageSrc && <><p><b>A. Chatbot</b></p><img src={imageSrc} alt="Bar Chart" /></>}
                </div>
                <div className="input-area">
                    <input type="text" value={message} onChange={e => setMessage(e.target.value)} onKeyPress={handleKeyPress} />
                    <button onClick={sendMessage}>Send</button>
                </div>
            </div>
        </div>
    );
};

export default App;