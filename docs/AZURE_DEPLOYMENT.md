# Azure Static Web Apps デプロイガイド

このドキュメントでは、Smallbase MVPアプリケーションをAzure Static Web AppsとAzure App Serviceにデプロイする方法を詳しく説明します。

## 目次

1. [アーキテクチャ概要](#アーキテクチャ概要)
2. [前提条件](#前提条件)
3. [デプロイ方法](#デプロイ方法)
4. [環境変数の設定](#環境変数の設定)
5. [CORS設定](#cors設定)
6. [トラブルシューティング](#トラブルシューティング)

---

## アーキテクチャ概要

このアプリケーションは以下の構成でデプロイします：

```
┌─────────────────────────────────────┐
│   Azure Static Web Apps             │
│   (フロントエンド)                   │
│   - frontend/index.html             │
│   - frontend/admin/*.html           │
└──────────────┬──────────────────────┘
               │ HTTPS
               │ API呼び出し
               ▼
┌─────────────────────────────────────┐
│   Azure App Service                 │
│   (FastAPI バックエンド)             │
│   - backend/main.py                 │
│   - backend/routers/*.py            │
└──────────────┬──────────────────────┘
               │ HTTPS
               │ API呼び出し
               ▼
┌─────────────────────────────────────┐
│   Supabase                          │
│   - 認証 (Auth)                     │
│   - データベース (PostgreSQL)       │
│   - ストレージ (Storage)            │
└─────────────────────────────────────┘
```

### デプロイ構成

- **フロントエンド**: Azure Static Web Apps
- **バックエンド**: Azure App Service (Python 3.11+)
- **データベース/認証**: Supabase（既存）

---

## 前提条件

### 必要なもの

1. **Azureアカウント**
   - [Azure Portal](https://portal.azure.com/)にアクセスできること
   - 有効なAzureサブスクリプション

2. **Azure CLI**
   - [Azure CLIのインストール](https://docs.microsoft.com/ja-jp/cli/azure/install-azure-cli)
   - バージョン確認: `az --version`

3. **GitHubアカウント**（推奨）
   - Azure Static Web AppsはGitHub Actionsと統合されています
   - または、Azure DevOps、GitLabも利用可能

4. **既存の設定**
   - Supabaseプロジェクトが設定済み
   - OpenAI APIキーを取得済み

### 必要な情報

デプロイ前に以下を準備してください：

- Supabase URL
- Supabase Anon Key
- Supabase Service Role Key
- OpenAI API Key

---

## デプロイ方法

### ステップ1: Azure CLIでログイン

```bash
# Azure CLIにログイン
az login

# サブスクリプションの確認
az account list --output table

# 使用するサブスクリプションを設定（必要に応じて）
az account set --subscription "サブスクリプション名またはID"
```

### ステップ2: リソースグループの作成

```bash
# リソースグループ名とリージョンを設定
RESOURCE_GROUP="smallbase-rg"
LOCATION="japaneast"  # または eastus, westeurope など

# リソースグループを作成
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### ステップ3: Azure App Service（バックエンド）のデプロイ

#### 3-1. App Serviceプランの作成

```bash
# App Serviceプラン名を設定
APP_SERVICE_PLAN="smallbase-plan"

# App Serviceプランを作成（Linux、Python 3.11）
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux
```

**注意**: `B1`はBasicプランです。本番環境では`S1`（Standard）以上を推奨します。

#### 3-2. Web Appの作成

```bash
# Web App名を設定（グローバルに一意である必要があります）
WEB_APP_NAME="smallbase-api-$(date +%s)"  # タイムスタンプで一意性を確保

# Web Appを作成
az webapp create \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --runtime "PYTHON:3.11"
```

#### 3-3. 環境変数の設定

```bash
# Supabase設定（実際の値に置き換えてください）
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your_anon_key"
SUPABASE_SERVICE_KEY="your_service_role_key"
OPENAI_API_KEY="sk-your_openai_key"

# 環境変数を設定
az webapp config appsettings set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    SUPABASE_URL="$SUPABASE_URL" \
    SUPABASE_KEY="$SUPABASE_KEY" \
    SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY" \
    OPENAI_API_KEY="$OPENAI_API_KEY" \
    ENVIRONMENT="production" \
    CORS_ORIGINS="https://your-static-web-app.azurestaticapps.net"
```

**重要**: `CORS_ORIGINS`は後でStatic Web AppsのURLに更新します。

#### 3-4. デプロイ設定の構成

```bash
# スタートアップコマンドを設定
az webapp config set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn main:app --bind 0.0.0.0:8000 --workers 2 --timeout 120"
```

#### 3-5. バックエンドコードのデプロイ

##### 方法A: ZIPデプロイ（推奨）

```bash
# バックエンドディレクトリに移動
cd backend

# 仮想環境を作成して依存関係をインストール
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install gunicorn

# 依存関係をローカルにインストール（デプロイ用）
pip install -r requirements.txt --target ./packages

# ZIPファイルを作成（.venvと__pycache__を除外）
zip -r ../deploy-backend.zip . \
  -x "*.git*" \
  -x "*__pycache__*" \
  -x "*.env*" \
  -x "*.pyc" \
  -x "venv/*"

# Azureにデプロイ
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --src ../deploy-backend.zip
```

##### 方法B: GitHub Actions（推奨）

`.github/workflows/deploy-backend.yml`を作成：

```yaml
name: Deploy Backend to Azure App Service

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install gunicorn
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
        publish-dir: './backend'
        startup-command: 'gunicorn main:app --bind 0.0.0.0:8000 --workers 2 --timeout 120'
```

GitHub Secretsに以下を設定：
- `AZURE_WEBAPP_NAME`: Web App名
- `AZURE_WEBAPP_PUBLISH_PROFILE`: 発行プロファイル（Azure Portalから取得）

### ステップ4: Azure Static Web Apps（フロントエンド）のデプロイ

#### 4-1. Static Web Appsリソースの作成

```bash
# Static Web Apps名を設定
STATIC_WEB_APP_NAME="smallbase-frontend"

# Static Web Appsを作成
az staticwebapp create \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Free
```

#### 4-2. フロントエンドコードの準備

フロントエンドのAPIベースURLを更新する必要があります。

`frontend/index.html`、`frontend/admin/index.html`、`frontend/admin/login.html`の以下の部分を更新：

```javascript
// 開発環境
const API_BASE_URL = 'http://localhost:8001';

// 本番環境（Azure App ServiceのURLに変更）
const API_BASE_URL = 'https://your-web-app-name.azurewebsites.net';
```

または、環境に応じて動的に設定：

```javascript
// 環境に応じたAPI URLの設定
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8001'
  : 'https://your-web-app-name.azurewebsites.net';
```

#### 4-3. デプロイ設定ファイルの作成

プロジェクトルートに `staticwebapp.config.json` を作成：

```json
{
  "routes": [
    {
      "route": "/",
      "serve": "/frontend/index.html",
      "statusCode": 200
    },
    {
      "route": "/admin",
      "serve": "/frontend/admin/index.html",
      "statusCode": 200
    },
    {
      "route": "/admin/login",
      "serve": "/frontend/admin/login.html",
      "statusCode": 200
    }
  ],
  "navigationFallback": {
    "fallback": "/frontend/index.html"
  },
  "responseOverrides": {
    "404": {
      "serve": "/frontend/index.html",
      "statusCode": 200
    }
  }
}
```

#### 4-4. GitHub Actionsでのデプロイ（推奨）

`.github/workflows/deploy-frontend.yml`を作成：

```yaml
name: Deploy Frontend to Azure Static Web Apps

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
      - 'staticwebapp.config.json'

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    name: Build and Deploy
    
    steps:
    - uses: actions/checkout@v3
      with:
        submodules: true
    
    - name: Build And Deploy
      id: builddeploy
      uses: Azure/static-web-apps-deploy@v1
      with:
        azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
        repo_token: ${{ secrets.GITHUB_TOKEN }}
        action: "upload"
        app_location: "/frontend"
        output_location: ""
        api_location: ""
```

**GitHub Secretsの設定**:
1. Azure PortalでStatic Web Appsを開く
2. 「Manage deployment token」をクリック
3. トークンをコピー
4. GitHubリポジトリの「Settings」→「Secrets」→「New repository secret」
5. `AZURE_STATIC_WEB_APPS_API_TOKEN`として保存

#### 4-5. 手動デプロイ（ZIP）

```bash
# フロントエンドをZIP化
cd frontend
zip -r ../deploy-frontend.zip .

# Azure CLIでデプロイ
az staticwebapp deploy \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-token "YOUR_DEPLOYMENT_TOKEN" \
  --app-location "/frontend" \
  --output-location ""
```

---

## 環境変数の設定

### Azure App Service（バックエンド）

Azure PortalまたはAzure CLIで設定：

```bash
az webapp config appsettings set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    SUPABASE_URL="https://your-project.supabase.co" \
    SUPABASE_KEY="your_anon_key" \
    SUPABASE_SERVICE_KEY="your_service_role_key" \
    OPENAI_API_KEY="sk-your_openai_key" \
    ENVIRONMENT="production" \
    CORS_ORIGINS="https://your-static-web-app.azurestaticapps.net"
```

### 環境変数の確認

```bash
# 設定された環境変数を確認
az webapp config appsettings list \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

---

## CORS設定

### バックエンド（Azure App Service）

Static Web AppsのURLをCORS設定に追加：

```bash
# Static Web AppsのURLを取得
STATIC_WEB_APP_URL=$(az staticwebapp show \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query defaultHostname -o tsv)

# CORS設定を更新
az webapp config appsettings set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    CORS_ORIGINS="https://${STATIC_WEB_APP_URL}"
```

### フロントエンド

フロントエンドのJavaScriptでAPI URLを設定：

```javascript
// 本番環境のAPI URL
const API_BASE_URL = 'https://your-web-app-name.azurewebsites.net';
```

---

## デプロイ後の確認

### 1. バックエンドの確認

```bash
# バックエンドのURLを取得
BACKEND_URL=$(az webapp show \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query defaultHostname -o tsv)

# ヘルスチェック
curl https://${BACKEND_URL}/health

# APIドキュメント
echo "API Docs: https://${BACKEND_URL}/docs"
```

### 2. フロントエンドの確認

```bash
# フロントエンドのURLを取得
FRONTEND_URL=$(az staticwebapp show \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query defaultHostname -o tsv)

echo "Frontend URL: https://${FRONTEND_URL}"
```

### 3. 動作確認

1. フロントエンドURLにアクセス
2. 管理画面でログイン
3. ファイルアップロードをテスト
4. チャット機能をテスト

---

## トラブルシューティング

### 問題1: CORSエラー

**症状**: ブラウザコンソールにCORSエラーが表示される

**解決方法**:
1. Azure App Serviceの環境変数`CORS_ORIGINS`にStatic Web AppsのURLが正しく設定されているか確認
2. URLの末尾にスラッシュがないか確認
3. `https://`プロトコルが正しく設定されているか確認

```bash
# CORS設定を確認
az webapp config appsettings list \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[?name=='CORS_ORIGINS']" -o table
```

### 問題2: 環境変数が読み込まれない

**症状**: アプリケーションが環境変数を読み込めない

**解決方法**:
1. Azure Portalで環境変数が正しく設定されているか確認
2. 環境変数名が大文字小文字を含めて正確か確認
3. App Serviceを再起動

```bash
# App Serviceを再起動
az webapp restart \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### 問題3: デプロイが失敗する

**症状**: GitHub Actionsやデプロイが失敗する

**解決方法**:
1. ログを確認
   ```bash
   az webapp log tail \
     --name $WEB_APP_NAME \
     --resource-group $RESOURCE_GROUP
   ```
2. `requirements.txt`に`gunicorn`が含まれているか確認
3. Pythonバージョンが3.11以上か確認

### 問題4: 静的ファイルが表示されない

**症状**: Static Web AppsでHTMLファイルが表示されない

**解決方法**:
1. `staticwebapp.config.json`の設定を確認
2. ファイルパスが正しいか確認
3. `app_location`と`output_location`が正しく設定されているか確認

### 問題5: API接続エラー

**症状**: フロントエンドからAPIに接続できない

**解決方法**:
1. フロントエンドの`API_BASE_URL`が正しいか確認
2. バックエンドのURLが正しいか確認
3. ネットワークセキュリティグループ（NSG）の設定を確認

---

## コスト最適化

### Free プラン

- **Azure Static Web Apps**: Freeプランで利用可能
- **Azure App Service**: Freeプラン（F1）は制限あり

### 推奨構成（本番環境）

- **Static Web Apps**: Standardプラン（月額約$9）
- **App Service**: Basic B1プラン（月額約$13）またはStandard S1プラン（月額約$70）

### コスト削減のヒント

1. 開発環境ではFreeプランを使用
2. 本番環境でのみStandardプランを使用
3. 使用していないリソースは停止
4. Azure Cost Managementでコストを監視

---

## セキュリティのベストプラクティス

### 1. 環境変数の保護

- 機密情報（APIキーなど）は環境変数として管理
- `.env`ファイルをGitにコミットしない
- Azure Key Vaultの使用を検討

### 2. HTTPSの強制

- Azure Static Web AppsとApp ServiceはデフォルトでHTTPS
- HTTPからHTTPSへのリダイレクトを設定

### 3. CORS設定

- 必要最小限のオリジンのみ許可
- ワイルドカード（`*`）は使用しない

### 4. 認証の強化

- Supabaseの認証機能を活用
- JWTトークンの有効期限を適切に設定

---

## 継続的デプロイ（CI/CD）

### GitHub Actionsワークフロー

上記の`.github/workflows/`に配置したワークフローファイルにより、以下の場合に自動デプロイされます：

- `main`ブランチへのプッシュ
- バックエンドコードの変更（`backend/**`）
- フロントエンドコードの変更（`frontend/**`）

### デプロイの確認

1. GitHubリポジトリの「Actions」タブでワークフローの実行状況を確認
2. Azure Portalでデプロイ履歴を確認
3. アプリケーションの動作をテスト

---

## 参考リンク

- [Azure Static Web Apps ドキュメント](https://docs.microsoft.com/ja-jp/azure/static-web-apps/)
- [Azure App Service ドキュメント](https://docs.microsoft.com/ja-jp/azure/app-service/)
- [FastAPI デプロイガイド](https://fastapi.tiangolo.com/deployment/)
- [Azure CLI リファレンス](https://docs.microsoft.com/ja-jp/cli/azure/)

---

## まとめ

このガイドに従うことで、Smallbase MVPアプリケーションをAzure Static Web AppsとAzure App Serviceにデプロイできます。

デプロイ後は、定期的にログを確認し、パフォーマンスとセキュリティを監視してください。

質問や問題が発生した場合は、Azure Portalのサポート機能を活用するか、Azureサポートに問い合わせてください。

