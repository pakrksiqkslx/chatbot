import React, { useState, useRef } from 'react';
import './App.css';
import Header from './components/Header/Header';
import ChatWindow from './components/ChatWindow/ChatWindow';
import Login from './components/Login/Login';
import Signup from './components/Signup/Signup';
import Sidebar from './components/Sidebar/Sidebar';
import RightToolbar from './components/RightToolbar/RightToolbar';
import Footer from './components/Footer/Footer';
import StudyPlan from './components/StudyPlan/StudyPlan';


let idCounter = 1;
function makeDefaultSession() {
  return {
    id: Date.now(),
    messages: [
      { id: idCounter++, from: 'bot', text: '안녕하세요! 무엇을 도와드릴까요?', ts: Date.now() },
    ],
    created: Date.now(),
  };
}

function App() {
  // 상태 관리
  const [sessions, setSessions] = useState([makeDefaultSession()]);
  const [currentSessionIdx, setCurrentSessionIdx] = useState(0);
  const currentSessionIdxRef = useRef(currentSessionIdx);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pendingSession, setPendingSession] = useState(null);
  const [user, setUser] = useState(null);
  const [showSignup, setShowSignup] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [currentPage, setCurrentPage] = useState('chat'); // 페이지 상태 추가

  React.useEffect(() => {
    currentSessionIdxRef.current = currentSessionIdx;
  }, [currentSessionIdx]);

  function handleSend(text) {
    if (pendingSession) {
      const newSession = {
        ...pendingSession,
        messages: [
          ...pendingSession.messages,
          { id: idCounter++, from: 'user', text, ts: Date.now() }
        ]
      };
      setSessions(prev => {
        const newSessionIdx = prev.length;
        const updated = [...prev, newSession];
        setCurrentSessionIdx(newSessionIdx);
        setPendingSession(null);
        setTimeout(() => {
          setSessions(prev2 => {
            const updated2 = [...prev2];
            const botMsg = { id: idCounter++, from: 'bot', text: `질문: "${text}" 에 대해 답변을 준비 중입니다. (예시 응답)`, ts: Date.now() };
            updated2[newSessionIdx].messages = [...updated2[newSessionIdx].messages, botMsg];
            return updated2;
          });
        }, 100);
        return updated;
      });
      return;
    }
    const idx = currentSessionIdxRef.current;
    setSessions(prev => {
      const updated = prev.map((session, i) =>
        i === idx
          ? { ...session, messages: [...session.messages, { id: idCounter++, from: 'user', text, ts: Date.now() }] }
          : session
      );
      return updated;
    });
    setTimeout(() => {
      setSessions(prev2 => {
        const updated2 = prev2.map((session, i) =>
          i === idx
            ? { ...session, messages: [...session.messages, { id: idCounter++, from: 'bot', text: `질문: "${text}" 에 대해 답변을 준비 중입니다. (예시 응답)`, ts: Date.now() }] }
            : session
        );
        return updated2;
      });
    }, 100);
  }

  function handleSelectSession(idx) {
    setCurrentSessionIdx(idx);
    setPendingSession(null);
  }

  function handleNewChat() {
    setPendingSession(makeDefaultSession());
  }

  function handleLogout() {
    setUser(null);
    setShowLogin(false);
    setShowSignup(false);
  }

  // 로그인 화면이 우선적으로 보이도록 분기
  if (!user && showLogin) {
    return (
      <Login
        onLogin={email => {
          setUser(email);
          setShowLogin(false);
        }}
        onSignup={() => {
          setShowSignup(true);
          setShowLogin(false);
        }}
      />
    );
  }

  // 회원가입 화면 분기
  if (!user && showSignup) {
    return (
      <Signup
        onSignup={email => {
          setUser(email);
          setShowSignup(false);
        }}
      />
    );
  }

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
      </div>
    );
  }

  // 챗봇 UI
  return (
    <div className="app-bg">
      <div className="app-center-box" style={sidebarOpen ? { paddingRight: 360 } : {}}>
        <Header title="AI 챗봇" />
        <ChatWindow
          messages={pendingSession ? pendingSession.messages : sessions[currentSessionIdx]?.messages}
          onSend={handleSend}
          sidebarOpen={sidebarOpen}
        />
      </div>
      <Sidebar
        open={sidebarOpen}
        sessions={sessions}
        currentSessionIdx={currentSessionIdx}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
      />
      <RightToolbar
        onToggle={() => setSidebarOpen((s) => !s)}
        sidebarOpen={sidebarOpen}
        onNewChat={handleNewChat}
        onLoginClick={() => {
          setShowLogin(true);
          setShowSignup(false);
        }}
        onLogoutClick={handleLogout}
        isLoggedIn={!!user}
      />
      <Footer 
        currentPage={currentPage}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}

export default App;
