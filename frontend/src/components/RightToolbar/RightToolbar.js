






import React from 'react';
import './RightToolbar.css';


export default function RightToolbar({ onToggle, sidebarOpen, onNewChat, onLoginClick }) {
  const toolbarClass = sidebarOpen ? 'rightbar-toolbar-22 rightbar-toolbar-22--left' : 'rightbar-toolbar-22';
  return (
    <nav className={toolbarClass} aria-label="오른쪽 툴바">
      <div className="rightbar-toolbar-22__top">
        <button className="rightbar-toolbar-22__btn" onClick={onToggle} aria-label="메뉴">
          <img src="/아이콘/세점.png" alt="메뉴" className="rightbar-toolbar-22__icon" />
        </button>
        <button className="rightbar-toolbar-22__btn" onClick={onNewChat} aria-label="새 채팅">
          <img src="/아이콘/연필.png" alt="새 채팅" className="rightbar-toolbar-22__icon" />
        </button>
      </div>
      <div className="rightbar-toolbar-22__bottom">
        {/* 로그인 버튼: 시계 버튼 위에 위치 */}
        <button className="rightbar-toolbar-22__btn" onClick={onLoginClick} aria-label="로그인">
          <img src="/아이콘/메인아이콘.png" alt="로그인" className="rightbar-toolbar-22__icon" />
        </button>
        <button className="rightbar-toolbar-22__btn" aria-label="활동">
          <img src="/아이콘/시계.png" alt="활동" className="rightbar-toolbar-22__icon" />
        </button>
        <button className="rightbar-toolbar-22__btn" aria-label="설정 및 도움말">
          <img src="/아이콘/설정.png" alt="설정 및 도움말" className="rightbar-toolbar-22__icon" />
        </button>
      </div>
    </nav>
  );
}
