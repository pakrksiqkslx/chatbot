import React from 'react';
import './ChatWindow.css';
import MessageList from '../MessageList/MessageList';
import MessageInput from '../MessageInput/MessageInput';

export default function ChatWindow({ messages, onSend, sidebarOpen }) {
  const chatWindowClass = sidebarOpen ? 'cb-chat-window sidebar-open' : 'cb-chat-window';
  
  return (
    <div className={chatWindowClass}>
      <MessageList messages={messages} />
      <MessageInput onSend={onSend} sidebarOpen={sidebarOpen} />
    </div>
  );
}
