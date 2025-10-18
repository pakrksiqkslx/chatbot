import React from 'react';
import './Footer.css';

export default function Footer({ currentPage, onPageChange }) {
  const handleStudyPlanClick = () => {
    if (currentPage === 'studyplan') {
      onPageChange('chat');
    } else {
      onPageChange('studyplan');
    }
  };

  return (
    <div className="cb-footer-hint">
      <div className="footer-left">
        <button 
          className="study-plan-btn" 
          onClick={handleStudyPlanClick}
        >
          {currentPage === 'studyplan' ? '채팅으로 돌아가기' : '교수용 수업계획서'}
        </button>
      </div>
      <div className="footer-center">
        Enter로 전송, Shift + Enter로 줄바꿈
      </div>
    </div>
  );
}
