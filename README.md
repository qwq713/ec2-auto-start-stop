# Seoul Office Hours

## SeoulOfficeHours 정책
- EC2 자원사용료 절감을 위해 평일 업무시간 외 EC2자원에 대해 사용을 중지하는 클라우드 정책

## SeoulOfficeHours.py
- SeoulOfficeHours 정책의 파이썬 코드 구현.
- CloudWatch 이벤트에 따라 EC2를 중지하거나 시작.


## SeoulOfficeHours.py 사용 방법
- EC2의 Schedule 태그값을 기반으로 정지 대상 EC2 및 시간을 스케줄링 할 수 있다.
- Schedule 태그값별 정지 시간
	- SEOUL-OFFICE-HOURS : 평일 18:00 정지 
	- SEOUL-OFFICE-HOURS-19 : 평일 19:00 정지
	- SEOUL-OFFICE-HOURS-20 : 평일 20:00 정지
	- SEOUL-OFFICE-HOURS-21: 평일 21:00 정지
	- SEOUL-OFFICE-HOURS-22: 평일 22:00 정지
	- 이외 값 : 대상 제외


## SeoulOfficeHours 정책에 대한 예외처리
- 예외처리가 필요한 경우 CSR을 접수하여 예외처리 수행
	- Schedule 태그의 값에 `EXCEPTION-YYYYMMDD` 값을 할당하여 언제까지 에외되는지 태깅
	- 예를들어 2022년 12월 31까지 예외처리가 필요한 경우 `EXCEPTION-20221231` 과같이 태깅
	- 예외처리 일자가 지난 경우 Schedule 값을 `SEOUL-OFFICE-HOURS`로  수동으로 원복


## SeoulOfficeHoursTagManager.py
- SeoulOfficeHours 정책에 예외처리된 대상을 수동으로 관리하기 힘들기에 파이썬 코드로 구현
- 현재 연월일(YYYYMMDD)과  예외처리된 대상의 Schedule 태그 값 ( EXCEPTION-YYYYMMDD) 중 YYYYMMDD 값을 비교하여 현재 날짜가 더 클 경우 ( 예외기간이 지난 경우에 해당 ) EXCEPTION-YYYYMMDD 값을 SEOUL-OFFICE-HOURS로 수정
- 예외처리가 필요한 경우 EXCEPTION-YYYYMMDD 형식에 맞춰 기입만 해주면 위 코드에 의해 ( 일 1회 자동 수행 ) 기한이 지난 EC2가 다시 스케줄링 대상으로 지정됨 

