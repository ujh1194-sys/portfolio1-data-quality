# 주문 데이터 품질 모니터링 프로젝트

## 프로젝트 개요

주문 데이터에서 NULL, 중복, 허용값 위반, 금액 오류, 날짜·시간 오류를 탐지하고,
문제의 심각도와 후속 조치를 정의한 데이터 품질 모니터링 프로젝트입니다.

pandas를 이용해 데이터 품질 검사를 수행하고,
규칙별 오류율과 주요 KPI를 Tableau 대시보드로 시각화했습니다.

## 사용 기술

- Python
- pandas
- CSV
- Tableau
- Git / GitHub

## 주요 결과

총 124건의 주문 데이터를 대상으로 데이터 품질 검사를 수행했습니다.

- 문제 행: 23건
- 문제 행 비율: 18.55%
- 우선 대응 행: 13건
- 확인 필요 행: 10건
- 실제 오류가 발생한 품질 규칙: 8개

주요 품질 문제는 다음과 같습니다.

- order_id 중복: 8행
- updated_at 시간 순서 위반: 4행
- customer_id NULL: 3행
- status 허용값 위반: 3행
- amount 0 이하: 2행
- payment_method 허용값 위반: 2행
- 미래 order_date: 2행
- amount NULL: 1행

각 오류 행에 품질 규칙, 심각도, 후속 조치를 연결하고,
규칙별 오류율과 전체 품질 KPI를 Tableau 대시보드로 시각화했습니다.

## 수행 내용

- pandas를 이용한 주문 데이터 품질 검사
- NULL, 중복, 허용값, 금액, 날짜·시간 규칙 검증
- 여러 품질 문제가 동시에 발생한 행의 오류 규칙 통합
- 문제 유형에 따른 심각도 및 운영 조치 정의
- 규칙별 오류 건수와 오류율 계산
- Tableau 기반 데이터 품질 모니터링 대시보드 구성
- Quality Rule Catalog를 이용한 품질 규칙 문서화
- Control Matrix를 이용한 품질 규칙과 업무 위험 연결
- Data Lineage를 이용한 데이터 처리 흐름 문서화

## 데이터 품질 규칙

주문 데이터의 품질을 확인하기 위해 다음 품질 차원을 기준으로 규칙을 정의했습니다.

- 완전성: 필수 데이터의 NULL 여부 확인
- 유일성: order_id 중복 여부 확인
- 유효성: 상태 코드, 결제수단, 금액, 날짜 값이 허용 기준에 맞는지 확인
- 일관성: 주문 생성 시각과 갱신 시각의 논리적 순서 확인

전체 품질 규칙은 `quality_rule_catalog.csv`에서 관리합니다.

## Control Matrix

데이터 품질 규칙을 실제 운영 위험과 연결해 관리했습니다.

각 규칙에 대해 다음 항목을 확인했습니다.

- Risk: 데이터 오류로 인해 발생할 수 있는 업무 위험
- Control: 위험을 발견하기 위한 품질 검사
- Threshold: 허용 가능한 오류 기준
- Actual Result: 실제 탐지된 오류 건수
- Status: 기준 충족 여부(PASS / FAIL)
- Action: 문제 발생 시 후속 조치

예를 들어 `order_id` 중복은 주문 건수와 매출의 중복 집계로 이어질 수 있으므로,
중복 허용 기준을 0건으로 두고 실제 탐지 결과를 확인했습니다.

전체 결과는 `control_matrix.csv`에서 관리합니다.

## Data Lineage

```text
portfolio1_orders_raw.csv
        ↓
dq_check.py를 이용한 데이터 품질 검사
        ↓
quality_operations_report.csv
quality_summary.csv
        ↓
quality_rule_monitoring.csv
quality_kpi.csv
        ↓
Tableau 시각화
        ↓
주문 데이터 품질 모니터링 대시보드