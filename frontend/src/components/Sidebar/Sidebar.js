import React from 'react';
import './Sidebar.css';

export default function Sidebar({ open, sessions = [], currentSessionIdx, onSelectSession, onNewChat }) {
  return (
    <div className={`sidebar${open ? ' sidebar--open' : ''}`}> 
      <div className="sidebar__menu">
        {/* 상단: 새 채팅/채팅목록/채팅 세션 */}
        <button className="sidebar__newchat-btn" onClick={onNewChat}>
          새 채팅
        </button>
        <div className="sidebar__item sidebar__item--title">채팅 목록</div>
        <div className="sidebar__sessions">
          {sessions
            .filter(session => session.messages.some(m => m.from === 'user'))
            .map((session, idx) => {
              const lastUserMsg = [...session.messages].reverse().find(m => m.from === 'user');
              const preview = lastUserMsg ? lastUserMsg.text.slice(0, 18) : '';
              return (
                <div
                  key={session.id}
                  className={`sidebar__session${idx === currentSessionIdx ? ' sidebar__session--active' : ''}`}
                  onClick={() => onSelectSession(idx)}
                >
                  {preview}
                </div>
              );
            })}
        </div>
      </div>
      {/* 하단: 활동/설정 및 도움말 */}
      <div className="sidebar__footer">
        <div className="sidebar__item">활동</div>
        <div className="sidebar__item">설정 및 도움말</div>
      </div>
    </div>
  );
}
