import unittest
import os
import json
import subprocess
import time
import urllib.request

# server.py を立ち上げるためのコマンド
SERVER_CMD = ["python", "server.py"]

# records.json のファイル名
DATA_FILE = "records.json"


class TestRecordsAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """テスト前にサーバを起動する"""
        # バックアップがあれば退避
        if os.path.exists(DATA_FILE):
            os.rename(DATA_FILE, DATA_FILE + ".bak")

        # サーバをバックグラウンドで起動
        cls.server_process = subprocess.Popen(SERVER_CMD)
        time.sleep(1)  # 少し待つ（サーバが立ち上がるため）

    @classmethod
    def tearDownClass(cls):
        """テスト後にサーバを停止する & ファイルを元に戻す"""
        cls.server_process.kill()
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        if os.path.exists(DATA_FILE + ".bak"):
            os.rename(DATA_FILE + ".bak", DATA_FILE)

    def get_url(self, path):
        return f"http://localhost:8000{path}"

    def test_01_empty(self):
        """最初は空なので GET /records は空配列"""
        with urllib.request.urlopen(self.get_url("/records")) as res:
            data = json.loads(res.read().decode())
            self.assertEqual(data, [])

    def test_02_post_and_get(self):
        """POST /records でデータ追加、その後 GET /records で確認"""
        rec = {
            "date": "2025-12-14",
            "category": "food",
            "amount": 100
        }
        req = urllib.request.Request(
            self.get_url("/records"),
            data=json.dumps(rec).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.getcode(), 201)

        # GET で追加分が取れる
        with urllib.request.urlopen(self.get_url("/records")) as res:
            data = json.loads(res.read().decode())
            # id はランダムなので category と amount だけ確認
            self.assertEqual(data[0]["category"], "food")
            self.assertEqual(data[0]["amount"], 100)

            # クラス変数として id を保存
            TestRecordsAPI.record_id = data[0]["id"]

    def test_03_total(self):
        """GET /records/total で合計を確認"""
        with urllib.request.urlopen(self.get_url("/records/total")) as res:
            data = json.loads(res.read().decode())
            self.assertEqual(data["total"], 100)

    def test_04_summary(self):
        """GET /records/summary でカテゴリ集計を確認"""
        with urllib.request.urlopen(self.get_url("/records/summary")) as res:
            data = json.loads(res.read().decode())
            self.assertEqual(data["food"], 100)

    def test_05_put(self):
        """PUT /records/{id} でレコードを編集する"""
        new_data = {"category": "snack", "amount": 150}
        req = urllib.request.Request(
            self.get_url(f"/records/{self.record_id}"),
            data=json.dumps(new_data).encode(),
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            self.assertEqual(data["category"], "snack")
            self.assertEqual(data["amount"], 150)

    def test_06_delete(self):
        """DELETE /records/{id} で削除する"""
        req = urllib.request.Request(
            self.get_url(f"/records/{self.record_id}"),
            method="DELETE"
        )
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            self.assertEqual(list(data.values())[0], self.record_id)


if __name__ == "__main__":
    unittest.main()
