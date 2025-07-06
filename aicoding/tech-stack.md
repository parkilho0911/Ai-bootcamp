# 기술 스택 문서

## 개발 환경
- 단일 HTML 파일 구조 (index.html)
- 모든 CSS와 JavaScript 코드를 HTML 파일 내에 포함
- 외부 의존성 최소화

## 프론트엔드 기술
### HTML5
- Canvas 요소 활용
- 웹 표준 준수
- 시맨틱 마크업

### CSS3
- Flexbox 레이아웃
- 반응형 디자인 (게임 캔버스 크기 조절)
- CSS 애니메이션 효과

### JavaScript (ES6+)
- 모듈화된 코드 구조
- 클래스 기반 객체지향 프로그래밍
- 이벤트 기반 프로그래밍

## 게임 엔진
### Phaser 3 (CDN 버전)
- 버전: 3.60.0
- CDN URL: https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.min.js
- MIT 라이선스 (무료 사용 가능)

#### Phaser 3 주요 기능
- 게임 물리 엔진 (Arcade Physics)
- 스프라이트 및 애니메이션 관리
- 충돌 감지 시스템
- 입력 처리 (키보드, 마우스)
- 사운드 시스템

## 에셋 관리
- Base64 인코딩된 이미지 리소스
- 인라인 SVG 그래픽
- 스프라이트 시트 최적화

## 성능 최적화
- 리소스 번들링
- 코드 미니파이
- 캔버스 렌더링 최적화
- 메모리 관리

## 브라우저 지원
- Chrome 최신 버전
- Firefox 최신 버전
- Safari 최신 버전
- Edge 최신 버전

## 개발 도구
- VS Code 또는 기타 텍스트 에디터
- 브라우저 개발자 도구
- Live Server (로컬 개발용)

## 버전 관리
- Git
- GitHub

## 배포 환경
- 정적 웹 호스팅 가능
- GitHub Pages 호스팅 지원
- CDN 활용 가능 