
import pandas as pd

# 1. 원본 데이터 읽기 및 기본 확인

df = pd.read_csv("portfolio1_orders_raw.csv")

print("데이터 크기:", df.shape)
print("컬럼 목록:", df.columns.tolist())
print(df.head())

print("\n컬럼별 NULL 개수:")
print(df.isna().sum())


# 2. 정상값 기준 설정 및 날짜 형식 변환

valid_status = ["completed", "cancelled", "pending"]
valid_payment_methods = ["card", "bank_transfer", "kakao_pay"]

df["order_date"] = pd.to_datetime(df["order_date"])
df["updated_at"] = pd.to_datetime(df["updated_at"])


# 3. 품질 규칙별 오류 검사 조건 설정

# customer_id NULL
customer_id_null = df["customer_id"].isna()

# status 허용값 위반
status_invalid = ~df["status"].isin(valid_status)

# amount NULL
amount_null = df["amount"].isna()

# amount 0 이하
amount_invalid = df["amount"] <= 0

# payment_method 허용값 위반
payment_invalid = ~df["payment_method"].isin(valid_payment_methods)

# 미래 order_date
future_date = df["order_date"] > pd.Timestamp("2026-09-21")

# updated_at 시간 순서 위반
time_invalid = df["updated_at"] < df["order_date"]

# order_id 중복
duplicate_id = df["order_id"].duplicated(keep=False)

# order_id NULL
order_id_null = df["order_id"].isna()


# 4. 품질 규칙별 오류 행 수 요약

quality_summary = pd.DataFrame({
    "품질 규칙": [
        "order_id NULL",
        "customer_id NULL",
        "status 허용값 위반",
        "amount NULL",
        "amount 0 이하",
        "payment_method 허용값 위반",
        "미래 order_date",
        "updated_at 시간 순서 위반",
        "order_id 중복"
    ],
    "오류 행 수": [
        order_id_null.sum(),
        customer_id_null.sum(),
        status_invalid.sum(),
        amount_null.sum(),
        amount_invalid.sum(),
        payment_invalid.sum(),
        future_date.sum(),
        time_invalid.sum(),
        duplicate_id.sum()
    ]
})

print("\n품질 요약 리포트:")
print(quality_summary)


# 5. 각 행의 위반 규칙과 오류 개수 기록
# 오류 이름은 빈 문자열, 오류 개수는 0으로 시작한다.
# 규칙을 위반할 때마다 오류 이름을 추가하고 개수를 1 증가시킨다.

df["issue_rules"] = ""
df["issue_count"] = 0

# customer_id NULL
df.loc[
    customer_id_null & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[customer_id_null, "issue_rules"] += "customer_id NULL"
df.loc[customer_id_null, "issue_count"] += 1


# status 허용값 위반
df.loc[
    status_invalid & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[status_invalid, "issue_rules"] += "status 허용값 위반"
df.loc[status_invalid, "issue_count"] += 1


# amount NULL
df.loc[
    amount_null & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[amount_null, "issue_rules"] += "amount NULL"
df.loc[amount_null, "issue_count"] += 1


# amount 0 이하
df.loc[
    amount_invalid & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[amount_invalid, "issue_rules"] += "amount 0 이하"
df.loc[amount_invalid, "issue_count"] += 1


# payment_method 허용값 위반
df.loc[
    payment_invalid & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[payment_invalid, "issue_rules"] += "payment_method 허용값 위반"
df.loc[payment_invalid, "issue_count"] += 1


# 미래 order_date
df.loc[
    future_date & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[future_date, "issue_rules"] += "미래 order_date"
df.loc[future_date, "issue_count"] += 1


# updated_at 시간 순서 위반
df.loc[
    time_invalid & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[time_invalid, "issue_rules"] += "updated_at 시간 순서 위반"
df.loc[time_invalid, "issue_count"] += 1


# order_id 중복
df.loc[
    duplicate_id & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[duplicate_id, "issue_rules"] += "order_id 중복"
df.loc[duplicate_id, "issue_count"] += 1


# order_id NULL
df.loc[
    order_id_null & (df["issue_rules"] != ""),
    "issue_rules"
] += " | "

df.loc[order_id_null, "issue_rules"] += "order_id NULL"
df.loc[order_id_null, "issue_count"] += 1


# 6. 오류가 하나 이상 있는 행 추출 및 전체 오류율 계산

issue_rows = df[df["issue_count"] > 0].copy()

total_rows = len(df)
issue_row_count = len(issue_rows)

# 전체 행 수가 0이면 0으로 나누지 않도록 처리한다.
if total_rows > 0:
    issue_rate = issue_row_count / total_rows * 100
else:
    issue_rate = 0

print("\n전체 품질 상태:")
print("전체 행 수:", total_rows)
print("오류가 하나 이상 있는 행 수:", issue_row_count)
print("오류 행 비율(%):", round(issue_rate, 2))

print("\n오류 상세 리포트:")
print(issue_rows[["order_id", "issue_rules", "issue_count"]])


# 품질 요약표 CSV 저장
quality_summary.to_csv(
    "quality_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

# 오류 상세표 CSV 저장
issue_rows.to_csv(
    "quality_issues.csv",
    index=False,
    encoding="utf-8-sig"
)


# 7. 운영 대응 우선순위 설정
# severity는 기존 CSV 및 Tableau와의 호환성을 위해 유지한 컬럼명이다.
# 실제로 분류하는 것은 운영 대응 우선순위(priority)이다.

issue_rows["severity"] = "확인 필요"

# 핵심 KPI에 직접 영향을 줄 가능성이 큰 오류 검사
high_priority_mask = (
    issue_rows["order_id"].duplicated(keep=False)
    | issue_rows["amount"].isna()
    | (issue_rows["amount"] <= 0)
    | (issue_rows["order_date"] > pd.Timestamp("2026-09-21"))
)

issue_rows.loc[
    high_priority_mask,
    "severity"
] = "우선 대응"

print("\n운영 우선순위별 오류 행 수:")
print(issue_rows["severity"].value_counts())


# 8. 오류 유형별 운영 조치 기록

issue_rows["action"] = ""


# order_id 중복
duplicate_action = issue_rows["order_id"].duplicated(keep=False)

issue_rows.loc[
    duplicate_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    duplicate_action,
    "action"
] += "중복 원본 확인 후 중복 제거/정정 검토"


# amount 관련 오류
amount_action = (
    issue_rows["amount"].isna()
    | (issue_rows["amount"] <= 0)
)

issue_rows.loc[
    amount_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    amount_action,
    "action"
] += "주문·결제 원본 금액 확인"


# 미래 order_date
date_action = issue_rows["order_date"] > pd.Timestamp("2026-09-21")

issue_rows.loc[
    date_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    date_action,
    "action"
] += "주문 생성 시각 및 적재 로직 확인"


# customer_id NULL
customer_action = issue_rows["customer_id"].isna()

issue_rows.loc[
    customer_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    customer_action,
    "action"
] += "고객 매핑 원본 확인"


# status 허용값 위반
status_action = ~issue_rows["status"].isin(valid_status)

issue_rows.loc[
    status_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    status_action,
    "action"
] += "상태 코드 변환 및 입력 로직 확인"


# payment_method 허용값 위반
payment_action = ~issue_rows["payment_method"].isin(
    valid_payment_methods
)

issue_rows.loc[
    payment_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    payment_action,
    "action"
] += "결제수단 코드 기준 확인"


# updated_at 시간 순서 위반
time_action = (
    issue_rows["updated_at"] < issue_rows["order_date"]
)

issue_rows.loc[
    time_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    time_action,
    "action"
] += "시간대 및 갱신 로직 확인"


# order_id NULL
order_id_action = issue_rows["order_id"].isna()

issue_rows.loc[
    order_id_action & (issue_rows["action"] != ""),
    "action"
] += " | "

issue_rows.loc[
    order_id_action,
    "action"
] += "주문 ID 원본 및 생성·적재 로직 확인"


# 9. 최종 운영 리포트 작성

final_report = issue_rows[
    [
        "order_id",
        "order_date",
        "customer_id",
        "status",
        "amount",
        "payment_method",
        "region",
        "updated_at",
        "issue_rules",
        "issue_count",
        "severity",
        "action"
    ]
].copy()


# 정렬을 위한 보조 컬럼 생성
# 우선 대응은 1, 확인 필요는 2로 설정한다.

final_report["severity_order"] = 2

final_report.loc[
    final_report["severity"] == "우선 대응",
    "severity_order"
] = 1


# 우선 대응 행을 먼저 표시한다.
# 동일한 우선순위에서는 오류 개수가 많은 행을 먼저 표시한다.

final_report = final_report.sort_values(
    ["severity_order", "issue_count"],
    ascending=[True, False]
)


# 정렬에 사용한 보조 컬럼 제거
final_report = final_report.drop(
    columns=["severity_order"]
)


# 최종 운영 리포트 CSV 저장
final_report.to_csv(
    "quality_operations_report.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n최종 운영 리포트:")
print(final_report)


# 10. Tableau 및 Excel용 규칙별 품질 모니터링 데이터 생성

rule_monitoring = quality_summary.copy()

rule_monitoring["전체 행 수"] = total_rows

if total_rows > 0:
    rule_monitoring["오류율(%)"] = (
        rule_monitoring["오류 행 수"]
        / total_rows
        * 100
    ).round(2)
else:
    rule_monitoring["오류율(%)"] = 0.0


# 오류 행 수가 많은 규칙부터 정렬
rule_monitoring = rule_monitoring.sort_values(
    "오류 행 수",
    ascending=False
)


# 규칙별 품질 모니터링 CSV 저장
rule_monitoring.to_csv(
    "quality_rule_monitoring.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n규칙별 품질 모니터링:")
print(rule_monitoring)


# 11. Tableau용 전체 품질 KPI 생성

# 오류가 발생한 품질 규칙 수
failed_rule_count = (
    quality_summary["오류 행 수"] > 0
).sum()

# 우선 대응 행 수
high_priority_count = (
    issue_rows["severity"] == "우선 대응"
).sum()

# 확인 필요 행 수
check_required_count = (
    issue_rows["severity"] == "확인 필요"
).sum()


quality_kpi = pd.DataFrame({
    "전체 행 수": [total_rows],
    "문제 행 수": [issue_row_count],
    "문제 행 비율(%)": [round(issue_rate, 2)],
    "우선 대응 행 수": [high_priority_count],
    "확인 필요 행 수": [check_required_count],
    "문제 발생 규칙 수": [failed_rule_count]
})


# 전체 품질 KPI CSV 저장
quality_kpi.to_csv(
    "quality_kpi.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n전체 품질 KPI:")
print(quality_kpi)

print("\nCSV 파일 5개 저장 완료")
