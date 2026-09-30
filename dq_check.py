import pandas as pd  # CSV 데이터를 표 형태로 다루기 위해 pandas를 불러온다.

# 주문 원본 CSV 파일을 읽어서 df라는 표로 저장한다.
df = pd.read_csv("portfolio1_orders_raw.csv")

# 데이터가 몇 행, 몇 열인지 확인한다.
print("데이터 크기:", df.shape)

# 어떤 컬럼들이 있는지 확인한다.
print("컬럼 목록:", df.columns.tolist())

# 데이터가 실제로 어떻게 생겼는지 앞의 5행만 확인한다.
print(df.head())

# 각 컬럼에 NULL 값이 몇 개 있는지 센다.
null_counts = df.isna().sum()

# 컬럼별 NULL 개수를 출력한다.
print("\n컬럼별 NULL 개수:")
print(null_counts)
    
# customer_id 또는 amount가 NULL인 주문 행만 추출한다.
# | 는 "또는(OR)"이라는 뜻이다.
null_issues = df[
    df["customer_id"].isna()
    | df["amount"].isna()
]

# 어떤 주문에서 NULL 문제가 발생했는지 확인한다.
print("\nNULL 품질 오류 행:")
print(
    null_issues[
        ["order_id", "customer_id", "amount"]
    ]
)

# status 컬럼에서 허용하는 정상값을 정의한다.
valid_status = ["completed", "cancelled", "pending"]

# 허용값 목록에 포함되지 않은 status 행만 추출한다.
status_issues = df[
    ~df["status"].isin(valid_status)
]

# 어떤 주문에서 잘못된 status가 들어왔는지 확인한다.
print("\nstatus 허용값 위반:")
print(
    status_issues[
        ["order_id", "status"]
    ]
)

# amount가 0 이하인 주문만 추출한다.
# 주문 금액은 0보다 커야 한다는 품질 규칙을 검사한다.
amount_issues = df[
    df["amount"] <= 0
]

# 어떤 주문에서 잘못된 금액이 들어왔는지 확인한다.
print("\namount 범위 위반:")
print(
    amount_issues[
        ["order_id", "amount"]
    ]
)

# order_id가 중복된 모든 행을 찾는다.
# keep=False를 쓰면 중복된 값의 모든 행을 보여준다.
duplicate_orders = df[
    df["order_id"].duplicated(keep=False)
]

# 중복 주문 ID와 관련 정보를 확인한다.
print("\n중복 order_id:")
print(
    duplicate_orders[
        ["order_id", "amount", "updated_at"]
    ].sort_values("order_id")
)

# order_date를 날짜 형식으로 변환한다.
# 문자열 상태보다 날짜 비교를 정확하게 하기 위해서다.
df["order_date"] = pd.to_datetime(df["order_date"])

# 기준일보다 미래인 주문만 추출한다.
future_date_issues = df[
    df["order_date"] > pd.Timestamp("2026-09-21")
]

# 미래 날짜로 기록된 주문을 확인한다.
print("\n미래 order_date 위반:")
print(
    future_date_issues[
        ["order_id", "order_date"]
    ]
)

# updated_at을 날짜+시간 형식으로 변환한다.
# 시간 순서를 정확하게 비교하기 위해서다.
df["updated_at"] = pd.to_datetime(df["updated_at"])

# updated_at이 order_date보다 과거인 행만 추출한다.
time_order_issues = df[
    df["updated_at"] < df["order_date"]
]

# 시간 순서가 잘못된 주문을 확인한다.
print("\nupdated_at 시간 순서 위반:")
print(
    time_order_issues[
        ["order_id", "order_date", "updated_at"]
    ]
)

# payment_method에서 허용하는 정상값을 정의한다.
valid_payment_methods = ["card", "bank_transfer", "kakao_pay"]

# 정상 결제수단 목록에 포함되지 않은 행만 추출한다.
payment_issues = df[
    ~df["payment_method"].isin(valid_payment_methods)
]

# 잘못된 결제수단이 들어간 주문을 확인한다.
print("\npayment_method 허용값 위반:")
print(
    payment_issues[
        ["order_id", "payment_method"]
    ]
)

# 각 품질 규칙별 오류 행 수를 하나의 표로 정리한다.
quality_summary = pd.DataFrame({
    "품질 규칙": [
        "customer_id NULL",
        "status 허용값 위반",
        "amount NULL",
        "amount 0 이하",
        "payment_method 허용값 위반",
        "미래 order_date",
        "updated_at 시간 순서 위반",
        "order_id 중복"
    ],

    # 각 규칙에서 탐지된 오류 행 수를 계산한다.
    "오류 행 수": [
        df["customer_id"].isna().sum(),
        (~df["status"].isin(valid_status)).sum(),
        df["amount"].isna().sum(),
        (df["amount"] <= 0).sum(),
        (~df["payment_method"].isin(valid_payment_methods)).sum(),
        (df["order_date"] > pd.Timestamp("2026-09-21")).sum(),
        (df["updated_at"] < df["order_date"]).sum(),
        df["order_id"].duplicated(keep=False).sum()
    ]
})

# 품질 규칙별 오류 건수 요약표를 출력한다.
print("\n품질 요약 리포트:")
print(quality_summary)

# order_id가 NULL인 행인지 검사한다.
order_id_null = df["order_id"].isna()

# 지금까지 만든 모든 품질 규칙을 하나로 합친다.
# | 는 OR이므로, 규칙 하나라도 위반하면 True가 된다.
issue_mask = (
    order_id_null
    | df["customer_id"].isna()
    | ~df["status"].isin(valid_status)
    | df["amount"].isna()
    | (df["amount"] <= 0)
    | ~df["payment_method"].isin(valid_payment_methods)
    | (df["order_date"] > pd.Timestamp("2026-09-21"))
    | (df["updated_at"] < df["order_date"])
    | df["order_id"].duplicated(keep=False)
)

# 품질 규칙을 하나 이상 위반한 실제 행만 추출한다.
issue_rows = df[issue_mask].copy()

# 전체 데이터 규모를 계산한다.
total_rows = len(df)

# 오류가 하나 이상 있는 행 수를 계산한다.
issue_row_count = len(issue_rows)

# 전체 중 문제가 있는 행의 비율을 계산한다.
issue_rate = issue_row_count / total_rows * 100

print("\n전체 품질 상태:")
print("전체 행 수:", total_rows)
print("오류가 하나 이상 있는 행 수:", issue_row_count)
print(f"오류 행 비율: {issue_rate:.2f}%")

# order_id NULL까지 포함해서 규칙별 오류 건수를 다시 정리한다.
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

    # 각 품질 규칙에서 탐지된 오류 행 수를 저장한다.
    "오류 행 수": [
        df["order_id"].isna().sum(),
        df["customer_id"].isna().sum(),
        (~df["status"].isin(valid_status)).sum(),
        df["amount"].isna().sum(),
        (df["amount"] <= 0).sum(),
        (~df["payment_method"].isin(valid_payment_methods)).sum(),
        (df["order_date"] > pd.Timestamp("2026-09-21")).sum(),
        (df["updated_at"] < df["order_date"]).sum(),
        df["order_id"].duplicated(keep=False).sum()
    ]
})

# 각 주문이 어떤 품질 규칙을 위반했는지 기록할 새 컬럼을 만든다.
# 처음에는 모든 행을 빈 문자열로 시작한다.
df["issue_rules"] = ""

# customer_id가 NULL이면 해당 오류 이름을 기록한다.
df.loc[
    df["customer_id"].isna(),
    "issue_rules"
] += "customer_id NULL | "

# status가 허용값 목록에 없으면 해당 오류 이름을 기록한다.
df.loc[
    ~df["status"].isin(valid_status),
    "issue_rules"
] += "status 허용값 위반 | "

# amount가 NULL이면 해당 오류 이름을 기록한다.
df.loc[
    df["amount"].isna(),
    "issue_rules"
] += "amount NULL | "

# amount가 0 이하이면 해당 오류 이름을 기록한다.
df.loc[
    df["amount"] <= 0,
    "issue_rules"
] += "amount 0 이하 | "

# 허용되지 않은 결제수단이면 해당 오류 이름을 기록한다.
df.loc[
    ~df["payment_method"].isin(valid_payment_methods),
    "issue_rules"
] += "payment_method 허용값 위반 | "

# 기준일보다 미래 주문이면 해당 오류 이름을 기록한다.
df.loc[
    df["order_date"] > pd.Timestamp("2026-09-21"),
    "issue_rules"
] += "미래 order_date | "

# 수정 시각이 주문 날짜보다 과거이면 해당 오류 이름을 기록한다.
df.loc[
    df["updated_at"] < df["order_date"],
    "issue_rules"
] += "updated_at 시간 순서 위반 | "

# order_id가 중복이면 중복 오류 이름을 기록한다.
df.loc[
    df["order_id"].duplicated(keep=False),
    "issue_rules"
] += "order_id 중복 | "

# 규칙별 오류 건수 요약표를 CSV 파일로 저장한다.
# utf-8-sig는 Excel에서 한글이 깨질 가능성을 줄이기 위해 사용한다.
quality_summary.to_csv(
    "quality_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

# 품질 규칙을 하나 이상 위반한 실제 주문 행들을 별도 CSV로 저장한다.
issue_rows.to_csv(
    "quality_issues.csv",
    index=False,
    encoding="utf-8-sig"
)

# 저장이 끝났다는 것을 터미널에서 확인한다.
print("\n파일 저장 완료:")
print("quality_summary.csv")
print("quality_issues.csv")

# 품질 오류가 있는 행의 order_id와 위반 규칙을 확인한다.
print("\n오류 규칙 표시:")
print(
    df.loc[
        df["issue_rules"] != "",
        ["order_id", "issue_rules"]
    ]
)

# order_id가 NULL인 경우도 품질 규칙 이름을 기록한다.
# 현재 데이터에는 0건이지만, 검사 로직에는 포함해야 한다.
df.loc[
    df["order_id"].isna(),
    "issue_rules"
] += "order_id NULL | "

# 마지막에 붙어 있는 " | "를 제거해서 보기 좋게 정리한다.
df["issue_rules"] = df["issue_rules"].str.rstrip(" |")

# 한 행이 품질 규칙을 몇 개 위반했는지 계산한다.
# 오류가 없으면 0, 오류 이름이 있으면 " | " 기준으로 나눠 개수를 센다.
df["issue_count"] = df["issue_rules"].apply(
    lambda x: 0 if x == "" else len(x.split(" | "))
)

# issue_rules가 비어 있지 않은 행만 다시 추출한다.
# 이번에는 issue_rules와 issue_count가 만들어진 뒤에 복사한다.
issue_rows = df[
    df["issue_rules"] != ""
].copy()

# 새 정보까지 포함해서 오류 상세 파일을 다시 저장한다.
issue_rows.to_csv(
    "quality_issues.csv",
    index=False,
    encoding="utf-8-sig"
)

# 결과를 확인한다.
print("\n오류 상세 리포트 확인:")
print(
    issue_rows[
        ["order_id", "issue_rules", "issue_count"]
    ]
)

print("\n오류 상세 행 수:", len(issue_rows))

# 모든 오류 행의 기본 우선순위를 "확인 필요"로 설정한다.
issue_rows["severity"] = "확인 필요"

# 핵심 KPI를 직접 왜곡할 가능성이 큰 오류가 포함된 행을 찾는다.
high_priority_mask = issue_rows["issue_rules"].str.contains(
    "order_id 중복|amount NULL|amount 0 이하|미래 order_date"
)

# 위 조건에 해당하는 행은 "우선 대응"으로 변경한다.
issue_rows.loc[
    high_priority_mask,
    "severity"
] = "우선 대응"

# 우선순위별 오류 행 수를 확인한다.
print("\n운영 우선순위별 오류 행 수:")
print(issue_rows["severity"].value_counts())

# 각 오류 행에 필요한 운영 조치를 누적해서 기록한다.
issue_rows["action"] = ""

# order_id 중복이면 중복 데이터 확인 조치를 추가한다.
issue_rows.loc[
    issue_rows["issue_rules"].str.contains("order_id 중복"),
    "action"
] += "중복 원본 확인 후 중복 제거/정정 검토 | "

# amount 관련 오류이면 원본 금액 확인 조치를 추가한다.
issue_rows.loc[
    issue_rows["issue_rules"].str.contains("amount NULL|amount 0 이하"),
    "action"
] += "주문·결제 원본 금액 확인 | "

# 미래 주문 날짜이면 생성 시각과 적재 로직 확인 조치를 추가한다.
issue_rows.loc[
    issue_rows["issue_rules"].str.contains("미래 order_date"),
    "action"
] += "주문 생성 시각 및 적재 로직 확인 | "

# customer_id가 비어 있으면 고객 매핑 원본 확인 조치를 추가한다.
issue_rows.loc[
    issue_rows["issue_rules"].str.contains("customer_id NULL"),
    "action"
] += "고객 매핑 원본 확인 | "

# status가 잘못됐으면 상태 코드 로직 확인 조치를 추가한다.
issue_rows.loc[
    issue_rows["issue_rules"].str.contains("status 허용값 위반"),
    "action"
] += "상태 코드 변환 및 입력 로직 확인 | "

# payment_method가 잘못됐으면 결제수단 기준을 확인한다.
issue_rows.loc[
    issue_rows["issue_rules"].str.contains("payment_method 허용값 위반"),
    "action"
] += "결제수단 코드 기준 확인 | "

# updated_at 시간 순서가 잘못됐으면 시간대와 갱신 로직을 확인한다.
issue_rows.loc[
    issue_rows["issue_rules"].str.contains("updated_at 시간 순서 위반"),
    "action"
] += "시간대 및 갱신 로직 확인 | "

# 마지막의 불필요한 구분자를 제거한다.
issue_rows["action"] = issue_rows["action"].str.rstrip(" |")

# 오류가 2개인 두 주문의 운영 조치가 모두 누적됐는지 확인한다.
print("\n다중 오류 조치 확인:")
print(
    issue_rows.loc[
        issue_rows["order_id"].isin(
            ["ORD-202609-041", "ORD-202609-118"]
        ),
        ["order_id", "issue_rules", "action"]
    ]
)

# 운영팀이 실제로 확인할 핵심 컬럼만 선택한다.
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

# 우선 대응 건이 위쪽에 오도록 정렬한다.
# 같은 우선순위에서는 오류 개수가 많은 행을 먼저 보여준다.
final_report["severity_order"] = final_report["severity"].map({
    "우선 대응": 1,
    "확인 필요": 2
})

# 운영 우선순위 → 오류 개수 순으로 정렬한다.
final_report = final_report.sort_values(
    ["severity_order", "issue_count"],
    ascending=[True, False]
)

# 정렬에만 사용한 보조 컬럼은 최종 파일에서 제거한다.
final_report = final_report.drop(
    columns=["severity_order"]
)

# 최종 운영 리포트를 CSV 파일로 저장한다.
# utf-8-sig는 Excel에서 한글이 깨지는 것을 줄이기 위해 사용한다.
final_report.to_csv(
    "quality_operations_report.csv",
    index=False,
    encoding="utf-8-sig"
)

# 파일이 정상적으로 만들어졌는지 확인한다.
print("\n최종 운영 리포트 저장 완료:")
print("quality_operations_report.csv")
print("최종 리포트 행 수:", len(final_report))

# 기존 품질 요약표를 복사해서 모니터링용 표를 만든다.
rule_monitoring = quality_summary.copy()

# 각 품질 규칙이 검사한 전체 데이터 행 수를 기록한다.
rule_monitoring["전체 행 수"] = total_rows

# 각 규칙의 오류 행 비율을 계산한다.
rule_monitoring["오류율(%)"] = (
    rule_monitoring["오류 행 수"]
    / rule_monitoring["전체 행 수"]
    * 100
).round(2)

# 오류 행 수가 많은 규칙부터 확인할 수 있도록 정렬한다.
rule_monitoring = rule_monitoring.sort_values(
    "오류 행 수",
    ascending=False
)

# Tableau나 Excel에서 사용할 수 있도록 CSV로 저장한다.
rule_monitoring.to_csv(
    "quality_rule_monitoring.csv",
    index=False,
    encoding="utf-8-sig"
)

# 결과를 터미널에서 확인한다.
print("\n규칙별 품질 모니터링:")
print(rule_monitoring)

print("\n모니터링 파일 저장 완료:")
print("quality_rule_monitoring.csv")

# 오류가 1건 이상 발생한 품질 규칙의 개수를 센다.
failed_rule_count = (
    quality_summary["오류 행 수"] > 0
).sum()

# 운영 우선순위별 행 수를 계산한다.
high_priority_count = (
    issue_rows["severity"] == "우선 대응"
).sum()

check_required_count = (
    issue_rows["severity"] == "확인 필요"
).sum()

# Tableau에서 KPI 숫자로 사용할 한 행짜리 표를 만든다.
quality_kpi = pd.DataFrame({
    "전체 행 수": [total_rows],
    "문제 행 수": [issue_row_count],
    "문제 행 비율(%)": [round(issue_rate, 2)],
    "우선 대응 행 수": [high_priority_count],
    "확인 필요 행 수": [check_required_count],
    "문제 발생 규칙 수": [failed_rule_count]
})

# KPI 데이터를 CSV로 저장한다.
quality_kpi.to_csv(
    "quality_kpi.csv",
    index=False,
    encoding="utf-8-sig"
)

# 결과를 확인한다.
print("\n전체 품질 KPI:")
print(quality_kpi)

print("\nKPI 파일 저장 완료:")
print("quality_kpi.csv")