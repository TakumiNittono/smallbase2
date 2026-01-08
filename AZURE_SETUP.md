# Azure Static Web Apps セットアップ完了

## 作成されたリソース

✅ **リソースグループ**: `smallbase-rg`  
✅ **Static Web Apps名**: `smallbase-frontend-15943`  
✅ **URL**: `https://mango-smoke-0484d9c00.4.azurestaticapps.net`

## デプロイトークン

以下のトークンをGitHub Secretsに設定してください：

```
39322b34f0979d207f56af74acc29144e17c4991d7624939b46ba6852272a5c304-be309d6c-d042-4087-89b0-0927d82f050300007200484d9c00
```

## GitHub Secretsの設定手順

1. GitHubリポジトリ（`https://github.com/TakumiNittono/smallbase2`）にアクセス
2. 「Settings」タブをクリック
3. 左サイドバーから「Secrets and variables」→「Actions」を選択
4. 「New repository secret」をクリック
5. 以下の情報を入力：
   - **Name**: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - **Secret**: 上記のデプロイトークンを貼り付け
6. 「Add secret」をクリック

## デプロイの実行

GitHub Secretsを設定後、以下のいずれかの方法でデプロイできます：

### 方法1: 自動デプロイ（推奨）
`main`ブランチに`frontend/`ディレクトリの変更をプッシュすると、自動的にデプロイされます。

### 方法2: 手動デプロイ
GitHubリポジトリの「Actions」タブから「Deploy Frontend to Azure Static Web Apps」ワークフローを手動実行できます。

## 確認方法

デプロイが完了したら、以下のURLにアクセスして確認できます：

**https://mango-smoke-0484d9c00.4.azurestaticapps.net**

## トラブルシューティング

### デプロイが失敗する場合

1. GitHub Secretsに`AZURE_STATIC_WEB_APPS_API_TOKEN`が正しく設定されているか確認
2. GitHub Actionsのログを確認（「Actions」タブから）
3. `staticwebapp.config.json`の設定が正しいか確認

### トークンを再取得する場合

```bash
az staticwebapp secrets list \
  --name smallbase-frontend-15943 \
  --resource-group smallbase-rg \
  --query "properties.apiKey" -o tsv
```

## 環境変数の設定

### ⚠️ 重要な注意点

**Azure Static Web Apps（フロントエンド）**: 
- 静的HTMLファイルのため、環境変数を直接使用できません
- フロントエンドコード内でAPI URLを環境に応じて動的に設定しています
- バックエンドのURLを設定する必要があります（下記参照）

**Azure App Service（バックエンド）**: 
- `.env`ファイルの内容を環境変数として設定する必要があります

### 1. バックエンドのApp Service作成（まだ作成していない場合）

```bash
RESOURCE_GROUP="smallbase-rg"
LOCATION="eastasia"  # Static Web Appsと同じリージョン

# App Serviceプランを作成
APP_SERVICE_PLAN="smallbase-plan"
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux

# Web Appを作成
WEB_APP_NAME="smallbase-api-$(date +%s | tail -c 6)"
az webapp create \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --runtime "PYTHON:3.11"

# スタートアップコマンドを設定
az webapp config set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn main:app --bind 0.0.0.0:8000 --workers 2 --timeout 120"
```

### 2. バックエンドの環境変数設定（Azure App Service）

バックエンドをデプロイする前に、以下の環境変数をAzure App Serviceに設定してください：

```bash
# バックエンドのApp Service名を設定（作成済みの場合）
WEB_APP_NAME="your-backend-app-name"
RESOURCE_GROUP="smallbase-rg"

# 環境変数を設定（.envファイルの内容を設定）
az webapp config appsettings set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    SUPABASE_URL="https://your-project.supabase.co" \
    SUPABASE_KEY="your_anon_key" \
    SUPABASE_SERVICE_KEY="your_service_role_key" \
    OPENAI_API_KEY="sk-your_openai_key" \
    ENVIRONMENT="production" \
    CORS_ORIGINS="https://mango-smoke-0484d9c00.4.azurestaticapps.net"
```

**必要な環境変数**:
- `SUPABASE_URL`: SupabaseプロジェクトのURL
- `SUPABASE_KEY`: Supabaseのanon public key
- `SUPABASE_SERVICE_KEY`: Supabaseのservice_role key（重要！）
- `OPENAI_API_KEY`: OpenAI APIキー
- `ENVIRONMENT`: `production`に設定
- `CORS_ORIGINS`: Static Web AppsのURL（上記のURL）

### 3. フロントエンドのAPI URL設定

フロントエンドのHTMLファイル内で、バックエンドのURLを設定する必要があります：

1. `frontend/index.html`、`frontend/admin/index.html`、`frontend/admin/login.html`を開く
2. `your-backend-app.azurewebsites.net`の部分を実際のバックエンドURLに変更

例：
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8001'
    : 'https://your-actual-backend-app.azurewebsites.net';
```

### 4. 環境変数の確認

設定した環境変数を確認するには：

```bash
az webapp config appsettings list \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

## 次のステップ

1. ✅ GitHub Secretsにトークンを設定
2. ✅ バックエンドの環境変数を設定（Azure App Service）
3. ✅ フロントエンドのAPI URLを設定
4. フロントエンドコードをプッシュしてデプロイをテスト
5. （オプション）カスタムドメインを設定

