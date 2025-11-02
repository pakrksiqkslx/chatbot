// API 기본 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// API 호출 유틸리티 함수
export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// 인증 관련 API
export const authAPI = {
  // 로그인
  login: async (email, password) => {
    return apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  // 회원가입
  signup: async (userData) => {
    return apiCall('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // 이메일 인증번호 발송
  sendVerificationEmail: async (email) => {
    return apiCall('/auth/send-verification', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  // 이메일 인증번호 확인
  verifyEmail: async (email, code) => {
    return apiCall('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    });
  },

  // 로그아웃
  logout: async () => {
    return apiCall('/auth/logout', {
      method: 'POST',
    });
  },

  // 토큰 검증
  verifyToken: async (token) => {
    return apiCall('/auth/verify', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },
};

export { API_BASE_URL };