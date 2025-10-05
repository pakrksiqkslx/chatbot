import React from 'react';
import './Header.css';

export default function Header({ title }) {
  return (
    <div className="header">
      <div className="header__left">
        <div className="header__avatar">
          <img src="/메인아이콘.png" alt="메인 아이콘" className="header__avatar-img" />
        </div>
        <div className="header__title-wrap">
          <div className="header__title">{title}</div>
          <div className="header__sub">항상 도와드릴 준비가 되어있습니다</div>
        </div>
      </div>
    </div>
  );
}
