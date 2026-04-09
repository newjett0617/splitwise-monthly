"""
專案設定，透過 pydantic-settings 從環境變數讀取。

支援兩種方式提供環境變數，機密不寫入程式碼：
- Doppler（推薦）
- 本機 .env 檔案
"""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExpenseRawConfig(BaseModel):
    """單筆費用的原始設定，key 對應 SPLITWISE_USER_IDS。"""
    description: str         # 費用名稱，支援 {month} 佔位符
    cost: int                # 總金額
    payer: str               # 付款人，對應 SPLITWISE_USER_IDS 的 key
    split: dict[str, int | float]  # 分攤對象與份數，程式自動正規化為比例


class Settings(BaseSettings):
    # Splitwise API
    splitwise_api_host: str
    splitwise_api_key: str

    # 群組
    splitwise_group_id_home: int

    # 幣別
    splitwise_currency_code: str

    # 成員名稱 -> user_id 對映（JSON）
    splitwise_user_ids: dict[str, int]

    # 費用清單（JSON）
    splitwise_expenses: list[ExpenseRawConfig]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
