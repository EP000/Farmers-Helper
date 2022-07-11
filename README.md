# Farmers-Helper

## 소개
초보 영농인을 위한 의사결정 서비스 "농부도우미"  
기술과 경험이 부족한 초보 영농인을 위해서 영농일지, 병해충 정보, 영농일지 작성등의 기능 제공  

### 영농일지 
- 사용자가 선택한 작물에 따라서 월 단위의 영농일지 제공

### 병해충 정보
- 사용자가 선택한 작물에 따라서 병해충 정보 제공

### 영농일지
- 날짜, 작업인원, 작업시간, 작업단계, 작업내용, 농약/비료 등의 정보 입력

## 데이터
- [농사로](https://fruit.nihhs.go.kr/com/openApi/farmWorkingPlanNewMain.do)
  - 크롤링
  - 작물 정보
- [국가농작물병해충관리시스템](https://ncpms.rda.go.kr/npms/Main.np)
  - API
  - 병해충 정보

## DB 구조
- mongoDB
<img src="https://user-images.githubusercontent.com/70522267/147641668-0334827e-76af-42a4-8c3b-ee4e71e9995e.png"  width="500"/>

## 환경
Ubuntu 18.04

## 대회
[2020 농림축산식품 공공 및 빅데이터 활용 창업경진대회](https://data.mafra.go.kr/contest/competition.do)  
아이디어 기획(팜맵데이터) 부분 최우수상 수상

