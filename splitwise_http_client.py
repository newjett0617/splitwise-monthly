"""
Splitwise API 的 HTTP client 封裝。

只封裝本專案實際用到的 API，完整文件參考：
https://dev.splitwise.com/
"""

import httpx

from config import settings


class SplitwiseClient:
    """Splitwise REST API client。"""

    def __init__(self):
        self._client = httpx.Client(
            base_url=settings.splitwise_api_host + "api/v3.0/",
            headers={
                "Authorization": f"Bearer {settings.splitwise_api_key}",
                "Content-Type": "application/json",
            },
        )

    def create_expense_by_shares(
        self,
        description: str,
        cost: float,
        group_id: int,
        currency_code: str,
        users: list[dict],
    ) -> dict:
        """
        建立費用（by shares 模式），自訂每個人的 paid_share / owed_share。

        注意：Splitwise API 回傳 200 不代表成功，需額外檢查 errors 欄位。

        Args:
            description:   費用名稱
            cost:          總金額
            group_id:      群組 ID
            currency_code: 幣別代碼（例如 "TWD"）
            users:         每位成員的分攤資訊，格式如下：
                           [
                               {"user_id": 123, "paid_share": "10000.00", "owed_share": "0.00"},
                               {"user_id": 456, "paid_share": "0.00",     "owed_share": "10000.00"},
                           ]

        Returns:
            建立成功的 expense 物件。

        Raises:
            httpx.HTTPStatusError: HTTP 層級錯誤
            ValueError:            Splitwise 回傳 errors 欄位
        """
        # 將 users list 展開為 API 要求的 users__{index}__{property} 格式
        body: dict = {
            "cost": f"{cost:.2f}",
            "description": description,
            "details": "Created by splitwise-monthly.\nhttps://github.com/newjett0617/splitwise-monthly",
            "group_id": group_id,
            "currency_code": currency_code,
        }
        for i, user in enumerate(users):
            body[f"users__{i}__user_id"] = user["user_id"]
            body[f"users__{i}__paid_share"] = user["paid_share"]
            body[f"users__{i}__owed_share"] = user["owed_share"]

        response = self._client.post("create_expense", json=body)
        response.raise_for_status()

        data = response.json()
        if data.get("errors"):
            raise ValueError(f"Splitwise 建立費用失敗: {data['errors']}")

        return data["expenses"][0]
