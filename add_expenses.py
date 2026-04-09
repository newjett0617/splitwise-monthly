"""
每月新增 Splitwise 費用的核心邏輯。

此模組為 stateless，不依賴任何外部設定，所有資料透過參數注入。
"""

from dataclasses import dataclass
from datetime import date

from splitwise_http_client import SplitwiseClient


@dataclass
class ExpenseConfig:
    """單筆費用的設定。"""
    description: str         # 費用名稱，支援 {month} 佔位符
    cost: int                # 總金額
    payer_id: int            # 付款人的 user_id
    split: dict[int, int | float]  # user_id -> 分攤份數，程式自動正規化為比例


def build_users(expense: ExpenseConfig) -> list[dict]:
    """
    將 ExpenseConfig 轉換為 Splitwise API 所需的 users payload。

    分攤邏輯：
    - split 值為整數份數（如 1, 1, 1），程式自動正規化為比例
    - 每人依比例四捨五入到小數點後兩位
    - 浮點數產生的餘數統一補在付款人身上，確保所有人的 owed_share 加總 = cost
    """
    # 正規化份數為比例
    total_shares = sum(expense.split.values())
    normalized = {uid: shares / total_shares for uid, shares in expense.split.items()}

    # 計算每人的 owed_share，先四捨五入
    owed: dict[int, float] = {}
    allocated = 0.0
    for uid, ratio in normalized.items():
        share = round(expense.cost * ratio, 2)
        owed[uid] = share
        allocated += share

    # 餘數補在付款人身上，確保加總等於 cost
    remainder = round(expense.cost - allocated, 2)
    owed[expense.payer_id] = owed.get(expense.payer_id, 0.0) + remainder

    return [
        {
            "user_id": uid,
            "paid_share": f"{expense.cost:.2f}" if uid == expense.payer_id else "0.00",
            "owed_share": f"{owed[uid]:.2f}",
        }
        for uid in owed
    ]


def add_expenses(
    expenses: list[ExpenseConfig],
    group_id: int,
    currency_code: str,
    client: SplitwiseClient,
) -> None:
    """
    依據費用清單逐筆建立當月費用。

    Args:
        expenses:      費用清單
        group_id:      目標群組 ID
        currency_code: 幣別代碼
        client:        Splitwise HTTP client
    """
    month = date.today().month

    for expense in expenses:
        description = expense.description.format(month=month)
        client.create_expense_by_shares(
            description=description,
            cost=expense.cost,
            group_id=group_id,
            currency_code=currency_code,
            users=build_users(expense),
        )
        print(f"✅ {description} ${expense.cost} 建立成功")
