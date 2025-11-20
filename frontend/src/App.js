import React, { useState, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';
import Header from './components/Header/Header';
import ChatWindow from './components/ChatWindow/ChatWindow';
import Login from './components/Login/Login';
import FindPassword from './components/Login/FindPassword';
import Signup from './components/Signup/Signup';
import VerifyEmail from './components/VerifyEmail/VerifyEmail';
import Sidebar from './components/Sidebar/Sidebar';
import RightToolbar from './components/RightToolbar/RightToolbar';
import Footer from './components/Footer/Footer';
import StudyPlan from './components/StudyPlan/StudyPlan';
import { LoadingOverlay } from './components/LoadingSpinner/LoadingSpinner';


// 고유한 메시지 ID 생성 함수
function generateMessageId() {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function makeDefaultSession() {
  return {
    id: Date.now(),
    messages: [
      { id: generateMessageId(), from: 'bot', text: '안녕하세요! 무엇을 도와드릴까요?', ts: Date.now() },
    ],
    created: Date.now(),
  };
}

function MainApp() {
  const navigate = useNavigate();
  // 상태 관리 - localStorage에서 세션 복원
  const [sessions, setSessions] = useState(() => {
    const savedSessions = localStorage.getItem('chatSessions');
    if (savedSessions) {
      try {
        return JSON.parse(savedSessions);
      } catch (e) {
        console.error('세션 복원 실패:', e);
      }
    }
    return [makeDefaultSession()];
  });
  const [currentSessionIdx, setCurrentSessionIdx] = useState(() => {
    const savedIdx = localStorage.getItem('currentSessionIdx');
    return savedIdx ? parseInt(savedIdx, 10) : 0;
  });
  const currentSessionIdxRef = useRef(currentSessionIdx);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pendingSession, setPendingSession] = useState(null);
  const [user, setUser] = useState(() => {
    // 초기 렌더링 시 localStorage에서 사용자 정보 복원
    const savedEmail = localStorage.getItem('userEmail');
    return savedEmail || null;
  });
  const [currentPage, setCurrentPage] = useState('chat');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [showFindPassword, setShowFindPassword] = useState(false);

  // 세션을 localStorage에 저장
  React.useEffect(() => {
    localStorage.setItem('chatSessions', JSON.stringify(sessions));
  }, [sessions]);

  // 현재 세션 인덱스를 localStorage에 저장
  React.useEffect(() => {
    localStorage.setItem('currentSessionIdx', currentSessionIdx.toString());
    currentSessionIdxRef.current = currentSessionIdx;
  }, [currentSessionIdx]);

  // 로그인 상태 확인 (localStorage와 user 상태 모두 체크)
  const isLoggedIn = (!!localStorage.getItem('authToken') && !!localStorage.getItem('access_token')) || !!user;
  if (!isLoggedIn) {
    if (showFindPassword) {
      return (
        <FindPassword onBack={() => setShowFindPassword(false)} />
      );
    }
    return (
      <Login
        onLogin={email => {
          setUser(email);
          // navigate는 필요 없음 - setUser가 리렌더링을 트리거함
        }}
        onSignup={() => {
          navigate('/signup');
        }}
        onBack={() => {
          navigate('/');
        }}
        onFindPassword={() => setShowFindPassword(true)}
      />
    );
  }

  // ...기존 챗봇 UI 렌더링 로직 (생략, 기존 코드 유지)...
  // StudyPlan 페이지
  if (currentPage === 'studyplan') {
    return (
      <div className="app-bg">
        <Header title="교수용 수업계획서" />
        <div style={{ 
          paddingTop: '0px', 
          paddingBottom: '45px', 
          minHeight: '100vh',
          boxSizing: 'border-box' 
        }}>
          <StudyPlan />
        </div>
        <Footer 
          currentPage={currentPage}
          onPageChange={setCurrentPage}
        />
        {isLoading && (
          <LoadingOverlay message={loadingMessage} />
        )}
      </div>
    );
  }

  // 메시지 전송 핸들러
  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    setIsLoading(true);
    setLoadingMessage('답변을 생성하고 있습니다...');

    try {
      // 로컬에 사용자 메시지 추가
      const userMessage = {
        id: generateMessageId(),
        from: 'user',
        text: text.trim(),
        ts: Date.now()
      };

      const currentMessages = sessions[currentSessionIdx]?.messages || [];
      const updatedMessages = [...currentMessages, userMessage];

      setSessions(prev => {
        const newSessions = [...prev];
        newSessions[currentSessionIdx] = {
          ...newSessions[currentSessionIdx],
          messages: updatedMessages
        };
        return newSessions;
      });

      // 백엔드 API 호출
      const { sendMessage } = await import('./utils/api');
      const response = await sendMessage(null, text.trim(), 3, true);

      // 봇 응답 추가
      const botMessage = {
        id: generateMessageId(),
        from: 'bot',
        text: response.answer || response.data?.answer || '응답을 받지 못했습니다.',
        sources: response.sources || response.data?.sources || [],
        ts: Date.now()
      };

      setSessions(prev => {
        const newSessions = [...prev];
        newSessions[currentSessionIdx] = {
          ...newSessions[currentSessionIdx],
          messages: [...updatedMessages, botMessage]
        };
        return newSessions;
      });

    } catch (error) {
      console.error('메시지 전송 실패:', error);
      alert('메시지 전송에 실패했습니다: ' + error.message);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  // 챗봇 UI
  return (
    <div className="app-bg">
      <div className="app-center-box" style={sidebarOpen ? { paddingRight: 360 } : {}}>
        <Header title="수업 플래너 챗봇" />
        <ChatWindow
          messages={pendingSession ? pendingSession.messages : sessions[currentSessionIdx]?.messages}
          onSend={handleSendMessage}
          sidebarOpen={sidebarOpen}
        />
      </div>
      <Sidebar
        open={sidebarOpen}
        sessions={sessions}
        currentSessionIdx={currentSessionIdx}
        onSelectSession={(idx) => {
          setCurrentSessionIdx(idx);
        }}
        onNewChat={() => {
          const newSession = makeDefaultSession();
          setSessions(prev => [newSession, ...prev]);
          setCurrentSessionIdx(0);
        }}
        onLogout={() => {
          setUser(null);
          localStorage.removeItem('authToken');
          localStorage.removeItem('userEmail');
          localStorage.removeItem('access_token');
          localStorage.removeItem('chatSessions');
          localStorage.removeItem('currentSessionIdx');
          navigate('/login');
        }}
      />
      <RightToolbar
        onToggle={() => setSidebarOpen((s) => !s)}
        sidebarOpen={sidebarOpen}
        onNewChat={() => {
          const newSession = makeDefaultSession();
          setSessions(prev => [newSession, ...prev]);
          setCurrentSessionIdx(0);
        }}
        onLoginClick={() => {
          navigate('/login');
        }}
        onLogoutClick={() => {
          setUser(null);
          localStorage.removeItem('authToken');
          localStorage.removeItem('userEmail');
          localStorage.removeItem('access_token');
          navigate('/login');
        }}
        isLoggedIn={!!user}
      />
      <Footer
        currentPage={currentPage}
        onPageChange={setCurrentPage}
      />
      {isLoading && (
        <LoadingOverlay message={loadingMessage} />
      )}
    </div>
  );
}

// 독립적인 로그인 컴포넌트
function LoginPage() {
  const navigate = useNavigate();
  
  return (
    <Login
      onLogin={email => {
        // 로그인 성공 후 메인 페이지로 이동
        navigate('/');
      }}
      onSignup={() => {
        navigate('/signup');
      }}
      onBack={() => {
        navigate('/');
      }}
    />
  );
}

// 독립적인 회원가입 컴포넌트
function SignupPage() {
  const navigate = useNavigate();
  
  return (
    <Signup
      onSignup={email => {
        // 회원가입 성공 후 메인 페이지로 이동
        navigate('/');
      }}
      onBack={() => {
        navigate('/login');
      }}
    />
  );
}

// 메인 App 컴포넌트 (라우터 설정)
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/login" element={<LoginPage />} />
  <Route path="/signup" element={<SignupPage />} />
  <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
