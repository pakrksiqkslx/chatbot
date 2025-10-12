import React from 'react';
import './MessageItem.css';

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function MessageItem({ message }) {
  const isUser = message.from === 'user';
  if (!isUser) {
    return (
      <div className="cb-message-row bot">
        <div className="cb-message-col">
          <div className="cb-message-bubble bot">
            <div className="cb-message-text">{message.text}</div>
          </div>
          <div className="cb-message-time bot-time">{formatTime(message.ts)}</div>
        </div>
      </div>
    );
  }
  return (
    <div className="cb-message-row user">
      <div className="cb-message-col user-col">
        <div className="cb-message-bubble user">
          <div className="cb-message-text">{message.text}</div>
        </div>
        <div className="cb-message-time user-time">{formatTime(message.ts)}</div>
      </div>
    </div>
  );
}
