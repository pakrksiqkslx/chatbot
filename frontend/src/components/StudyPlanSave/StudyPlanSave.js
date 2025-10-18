import React from 'react';
import './StudyPlanSave.css';

export default function StudyPlanSave({ 
  savedPlans, 
  selectedPlanId, 
  onSelectPlan, 
  onDeletePlan, 
  onNewPlan 
}) {
  return (
    <div className="study-plan-right">
      <div className="saved-plans-sidebar">
        <div className="saved-plans-header">
          <h3>저장된 수업계획서</h3>
          <button className="new-plan-btn" onClick={onNewPlan}>
            + 새 계획서
          </button>
        </div>
        
        {savedPlans.length === 0 ? (
          <div className="no-plans-message">
            저장된 수업계획서가 없습니다.<br/>
            새 계획서를 작성해보세요.
          </div>
        ) : (
          <div className="saved-plans-list">
            {savedPlans.map((plan) => (
              <div 
                key={plan.id} 
                className={`saved-plan-item ${selectedPlanId === plan.id ? 'selected' : ''}`}
                onClick={() => onSelectPlan(plan.id)}
              >
                <span className="plan-title">{plan.title}</span>
                <span className="plan-date">{plan.createdAt}</span>
                <button 
                  className="delete-plan-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeletePlan(plan.id);
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
