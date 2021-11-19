# EC2 인스턴스에 Seoul Office Hours 적용

## Seoul Office Hours 정책

- 업무시간( SeoulOfficeHours )외 시간에 유휴 컴퓨팅 자원 ( 개발 및 테스트 용도의 EC2 )을 중지하는 정책
- 평일 업무시간 08:00 ~ 18:00 이외 및 주말 시간에 유휴 자원을 중지함으로써 자원 사용량 절감

## 기능

- 대상 : DEV / QAS 계정 EC2 인스턴스
- 내용 :
  - 평일 08:00 ~ 18:00 업무시간 외 개발 및 테스트 용도 EC2 인스턴스 중지
- 기능 :
  - 평일 08:00 에 Schedule 태그에 따라 EC2인스턴스 시작
  - 평일 18:00/19:00/20:00/21:00/22:00 에 Schedule 태그에 따라 EC2인스턴스 중지

## AWS 서비스 구성

- AWS 서비스

  - lambda function
  - cloudwatch eventbridge

- lambda 구성 시 주의사항
  - lambda 서비스는 EC2인스턴스의 태그값을 이용하여 로직이 수행되므로 lambda의 타임존은 한국시간으로 설정한다.
    - lambda function의 환경변수 탭에서 TZ = 'Asia/Seoul' 로 반드시 설정할 것
    - lambda 서비스를 트리거하는 EventBridge의 cron 표현식은 GMT(UTC+09:00)기준으로 작성한다.
      - cron 표현식은 GMT 시간만 지원한다.
      - 즉 EventBridge의 cron 표현식은 GMT 기준(+09:00) 이므로 시작시간 및 요일에 대해 설정시 주의할 것
    - cron 패턴식 예시.1) 한국시간 월요일 ~ 금요일 아침 08:00 마다 호출
      - cron(0 23 ? _ SUN-THU _)
      - 한국시간으로 월요일 ~ 금요일 아침 08:00 은 GMT 기준 일요일 ~ 목요일 저녁 23:00 이다.
    - cron 패턴식 예시.2) 한국시간 월요일 ~ 금요일 저녁 18:00 마다 호출
      - cron(0 9 ? _ MON-FRI _) / Enable
      - 한국시간으로 월요일 ~ 금요일 저녁 18:00는 GMT 기준으로 월요일 ~ 금요일 09:00 이다.

## 사용 방법 (태그 설정)

- EC2 인스턴스의 TAG설정정보를 기반으로 자동으로 lambda에서 대상을 선정한다.
- TAG 정보
  - KEY : Schedule
  - Values : SEOUL-OFFICE-HOURS ( 기동시간 : 평일 08:00 ~ 18:00 ) => Default
    SEOUL-OFFICE-HOURS-19 ( 기동시간 : 평일 08:00 ~ 19:00 )
    SEOUL-OFFICE-HOURS-20 ( 기동시간 : 평일 08:00 ~ 20:00 )
    SEOUL-OFFICE-HOURS-21 ( 기동시간 : 평일 08:00 ~ 21:00 )
    SEOUL-OFFICE-HOURS-22 ( 기동시간 : 평일 08:00 ~ 22:00 )
    EXCEPTION-YYYYMMDD => 예외 ( 서버 시작/중지 대상에서 YYYYMMDD까지 제외 )

## 추가 기능 구현사항

1. SeoulOfficeHoursTagManager.py : 업무 프로세스 개선

- 개발목적 : DEV / QAS SeoulOfficeHours 관리가 힘듬

- 원인분석 : CSR 요청을 받아서 Exception 처리 후 , 원래대로 SeoulOfficeHour 태그 설정하는 부분을 수동을 직접 확인하고 수정해야한다.
  - 업무 프로세스 ( AS-IS )
    1. 예외신청 ( ex: 21년 11월 30일까지 예외해주세요. by csr or email)
    2. TAG 변경 -> EXCEPTION-20211130
    3. 21년 11월 30일 이후 EXCEPTION-20211130 콘솔에서 발견
    4. TAG 변경 -> SEOUL-OFFICE-HOURS
- 개발목적 : 1-2를 제외한 3-4에 대한 자동화 즉 EXCEPTION-YYYYMMDD 정보가 현재날짜보다 이후일 경우 SEOUL-OFFICE-HOURS 로 변경한다.

- 개선이후 업무 프로세스 ( TO-BE)
  1. 예외신청 ( ex: 21년 11월 30일까지 예외해주세요. by csr or email)
  2. TAG 변경 -> EXCEPTIO-20211130
  3. AS-IS 3-4 프로세스는 아침 7시에 자동으로 수행.
