import React from 'react';
import './ChatWindow.css';
import MessageList from '../MessageList/MessageList';
import MessageInput from '../MessageInput/MessageInput';

export default function ChatWindow({ messages, onSend, sidebarOpen }) {
  return (
    <div className="cb-chat-window">
      <MessageList messages={messages} />
      <MessageInput onSend={onSend} sidebarOpen={sidebarOpen} />
    </div>
  );
}
