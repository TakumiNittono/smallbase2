"""
API動作確認用テストスクリプト
"""
import requests
import json
import os
from pathlib import Path

API_BASE_URL = "http://localhost:8001"


def test_health_check():
    """ヘルスチェックテスト"""
    print("=" * 50)
    print("1. ヘルスチェックテスト")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        assert response.status_code == 200
        print("✅ ヘルスチェック: 成功\n")
        return True
    except Exception as e:
        print(f"❌ ヘルスチェック: 失敗 - {e}\n")
        return False


def test_login(email, password):
    """ログインテスト"""
    print("=" * 50)
    print("2. ログインテスト")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"アクセストークン: {data['access_token'][:50]}...")
            print(f"ユーザー情報: {json.dumps(data['user'], indent=2, ensure_ascii=False)}")
            print("✅ ログイン: 成功\n")
            return data['access_token']
        else:
            print(f"レスポンス: {response.json()}")
            print("❌ ログイン: 失敗\n")
            return None
    except Exception as e:
        print(f"❌ ログイン: エラー - {e}\n")
        return None


def test_get_files(token):
    """ファイル一覧取得テスト"""
    print("=" * 50)
    print("3. ファイル一覧取得テスト")
    print("=" * 50)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/files",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            files = response.json()
            print(f"ファイル数: {len(files)}")
            if files:
                print("ファイル一覧:")
                for file in files:
                    print(f"  - {file['filename']} (ID: {file['id']})")
            else:
                print("ファイルはありません")
            print("✅ ファイル一覧取得: 成功\n")
            return files
        else:
            print(f"レスポンス: {response.json()}")
            print("❌ ファイル一覧取得: 失敗\n")
            return []
    except Exception as e:
        print(f"❌ ファイル一覧取得: エラー - {e}\n")
        return []


def test_upload_file(token, file_path):
    """ファイルアップロードテスト"""
    print("=" * 50)
    print("4. ファイルアップロードテスト")
    print("=" * 50)
    
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}\n")
        return None
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            response = requests.post(
                f"{API_BASE_URL}/admin/upload",
                headers={"Authorization": f"Bearer {token}"},
                files=files
            )
        
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"アップロード結果: {json.dumps(data, indent=2, ensure_ascii=False)}")
            print("✅ ファイルアップロード: 成功\n")
            return data.get('id')
        else:
            print(f"レスポンス: {response.json()}")
            print("❌ ファイルアップロード: 失敗\n")
            return None
    except Exception as e:
        print(f"❌ ファイルアップロード: エラー - {e}\n")
        return None


def test_delete_file(token, file_id):
    """ファイル削除テスト"""
    print("=" * 50)
    print("5. ファイル削除テスト")
    print("=" * 50)
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/admin/files/{file_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"削除結果: {json.dumps(data, indent=2, ensure_ascii=False)}")
            print("✅ ファイル削除: 成功\n")
            return True
        else:
            print(f"レスポンス: {response.json()}")
            print("❌ ファイル削除: 失敗\n")
            return False
    except Exception as e:
        print(f"❌ ファイル削除: エラー - {e}\n")
        return False


def main():
    """メイン関数"""
    print("\n" + "=" * 50)
    print("Smallbase MVP API 動作確認テスト")
    print("=" * 50 + "\n")
    
    # 1. ヘルスチェック
    if not test_health_check():
        print("❌ サーバーが起動していません。先にサーバーを起動してください。")
        return
    
    # 2. ログイン（環境変数から取得、または入力）
    email = os.getenv("TEST_EMAIL", input("管理者メールアドレスを入力してください: "))
    password = os.getenv("TEST_PASSWORD", input("パスワードを入力してください: "))
    
    token = test_login(email, password)
    if not token:
        print("❌ ログインに失敗しました。Supabaseの設定を確認してください。")
        return
    
    # 3. ファイル一覧取得
    files = test_get_files(token)
    
    # 4. ファイルアップロード（オプション）
    upload_test = input("\nファイルアップロードテストを実行しますか？ (y/n): ")
    if upload_test.lower() == 'y':
        file_path = input("アップロードするファイルのパスを入力してください: ")
        file_id = test_upload_file(token, file_path)
        
        # 5. ファイル削除（オプション）
        if file_id:
            delete_test = input("\nファイル削除テストを実行しますか？ (y/n): ")
            if delete_test.lower() == 'y':
                test_delete_file(token, file_id)
        
        # 再度ファイル一覧を取得して確認
        print("\n" + "=" * 50)
        print("更新後のファイル一覧")
        print("=" * 50)
        test_get_files(token)
    
    print("\n" + "=" * 50)
    print("動作確認テスト完了")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()

