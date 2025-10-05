import React, { useState } from 'react';
import './MessageInput.css';

export default function MessageInput({ onSend, sidebarOpen }) {
  const [text, setText] = useState('');

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  function send() {
    const t = text.trim();
    if (!t) return;
    onSend(t);
    setText('');
  }

  return (
    <div className={`cb-message-input${sidebarOpen ? ' sidebar-open' : ''}`}>
      <div className="cb-input-wrap">
        <textarea
          placeholder="메시지를 입력하세요..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
        />
        <button className="cb-send" onClick={send} aria-label="전송">➤</button>
      </div>
    </div>
  );
}
