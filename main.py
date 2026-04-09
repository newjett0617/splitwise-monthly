"""
入口程式。

負責從 config 讀取設定，將名稱對映轉換為 user_id，再注入 add_expenses。
"""

from add_expenses import ExpenseConfig, add_expenses
from config import settings
from splitwise_http_client import SplitwiseClient


def build_expenses() -> list[ExpenseConfig]:
    """
    將 settings 中的 ExpenseRawConfig（含名稱）轉換為 ExpenseConfig（含 user_id）。

    SPLITWISE_USER_IDS 的 key 必須與 SPLITWISE_EXPENSES 中的 payer / split key 一致。
    """
    uid = settings.splitwise_user_ids

    return [
        ExpenseConfig(
            description=raw.description,
            cost=raw.cost,
            payer_id=uid[raw.payer],
            split={uid[name]: ratio for name, ratio in raw.split.items()},
        )
        for raw in settings.splitwise_expenses
    ]


def main():
    add_expenses(
        expenses=build_expenses(),
        group_id=settings.splitwise_group_id_home,
        currency_code=settings.splitwise_currency_code,
        client=SplitwiseClient(),
    )


if __name__ == "__main__":
    main()
