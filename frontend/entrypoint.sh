#!/bin/sh
# nginx 시작 전 환경변수를 JavaScript로 주입하는 스크립트

# 환경변수에서 REACT_APP_API_URL 가져오기 (없으면 기본값 사용)
API_URL="${REACT_APP_API_URL:-http://localhost:5000/api}"

# env-config.js 파일 생성
cat > /usr/share/nginx/html/env-config.js <<EOF
window._env_ = {
  REACT_APP_API_URL: '${API_URL}'
};
EOF

echo "환경변수 설정 완료: REACT_APP_API_URL=${API_URL}"

# nginx 실행
exec nginx -g 'daemon off;'



