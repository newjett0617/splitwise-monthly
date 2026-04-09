# splitwise-monthly

每月自動透過 Splitwise API 新增固定費用，由 GitHub Actions 排程執行。

## 功能

每月自動在指定群組建立費用，費用項目與金額完全由環境變數定義，程式碼本身不含任何個人資訊。

## 專案結構

```
splitwise-monthly/
├── main.py                  # 入口，讀取 config 並注入 add_expenses
├── add_expenses.py          # 核心邏輯（stateless），不依賴任何外部設定
├── splitwise_http_client.py # Splitwise API client 封裝
├── config.py                # 設定，從環境變數讀取並驗證
├── .env.example             # 環境變數範本（使用 .env 方式時參考）
└── pyproject.toml
```

## 環境設定

支援兩種方式提供環境變數：

- **Doppler**（推薦）：使用 [Doppler](https://doppler.com) 管理，本機執行 `doppler run -- uv run main.py`
- **`.env`**：複製 `.env.example` 為 `.env` 並填入實際值，執行 `uv run main.py`

### 環境變數說明

| 變數                        | 說明                                                       |
|---------------------------|----------------------------------------------------------|
| `SPLITWISE_API_HOST`      | Splitwise API 位址，固定為 `https://secure.splitwise.com/`     |
| `SPLITWISE_API_KEY`       | Splitwise API key，至 https://secure.splitwise.com/apps 申請 |
| `SPLITWISE_GROUP_ID_HOME` | 費用要加入的群組 ID                                              |
| `SPLITWISE_CURRENCY_CODE` | 幣別代碼（例如 `TWD`、`USD`）                                     |
| `SPLITWISE_USER_IDS`      | 成員名稱與 user_id 的對映（JSON）                                  |
| `SPLITWISE_EXPENSES`      | 費用清單（JSON），名稱須對應 `SPLITWISE_USER_IDS` 的 key              |

### `SPLITWISE_USER_IDS` 格式

```json
{
  "member_a": 12345,
  "member_b": 67890
}
```

### `SPLITWISE_EXPENSES` 格式

```json
[
  {
    "description": "{month}月項目名稱",
    "cost": 1000,
    "payer": "member_b",
    "split": {
      "member_a": 1
    }
  }
]
```

- `description`：支援 `{month}` 佔位符，執行時自動替換為當月月份
- `payer`：付款人，須對應 `SPLITWISE_USER_IDS` 的 key
- `split`：分攤對象與份數，**key 須對應 `SPLITWISE_USER_IDS` 的 key**，程式自動正規化為比例
    - 三人平分：`{"a": 1, "b": 1, "c": 1}`
    - 某人獨付：`{"a": 1}`
    - 若金額除不盡，餘數自動補在付款人身上

## 本機執行

使用 Doppler：

```bash
doppler run -- uv run main.py
```

使用 `.env`：

```bash
cp .env.example .env  # 填入實際值
uv run main.py
```

## GitHub Actions

每月 1 日 UTC 00:00（台灣時間 08:00）自動執行。

在 GitHub repo 的 **Settings → Secrets and variables → Actions** 中新增一個 Secret：

- `DOPPLER_TOKEN`：至 Doppler Dashboard 的 **Access → Service Tokens** 建立

## 調整費用

所有調整只需在 Doppler Dashboard 修改，不需要改任何程式碼。

**修改金額**：更新 `SPLITWISE_EXPENSES` 中對應項目的 `cost`

**新增項目**：在 `SPLITWISE_EXPENSES` 的 JSON 陣列加一筆

**移除項目**：從 `SPLITWISE_EXPENSES` 的 JSON 陣列刪掉對應項目

**新增成員**：在 `SPLITWISE_USER_IDS` 加一組 key/value，再更新 `SPLITWISE_EXPENSES` 的 split
