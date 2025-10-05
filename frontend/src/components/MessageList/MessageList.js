import React, { useEffect, useRef } from 'react';
import './MessageList.css';
import MessageItem from '../MessageItem/MessageItem';

export default function MessageList({ messages }) {
  const ref = useRef();
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [messages]);

  return (
    <div className="cb-message-list" ref={ref}>
      {messages.map((m) => (
        <MessageItem key={m.id} message={m} />
      ))}
    </div>
  );
}
