from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse

import uuid

DATA_FILE = "records.json"


def load_records():
    """
    保存されている家計簿データを読み込む。
    ファイルが存在しなければ空のリストを返す。
    :return: レコードのリスト (辞書のリスト)
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # ファイルがなければ、空の家計簿データとみなす
        return []


def save_records(records):
    """
    家計簿データ (リスト) をファイルに保存する。
    :param records: レコードのリスト (辞書のリスト)
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


class MyHandler(BaseHTTPRequestHandler):
    """HTTP リクエストを受け取り、家計簿データの取得・追加を処理するハンドラ"""

    def _set_headers(self, status=200):
        """レスポンスヘッダー (ステータスコード + JSON + UTF-8) をセットする共通処理"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        # React からアクセスできるように CORS を許可
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods",
                         "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        """CORS プリフライトリクエストに対応"""
        self._set_headers()

    def do_GET(self):
        """
        GET /records — 全レコードを返す
        GET /records/total - 合計金額を返す
        GET /records/summary - カテゴリ別集計を返す
        """
        parsed = urlparse(self.path)

        # 全レコード取得
        if parsed.path == "/records":
            records = load_records()
            self._set_headers(200)
            self.wfile.write(json.dumps(
                records, ensure_ascii=False).encode("utf-8"))
            return

        # 合計金額取得
        if parsed.path == "/records/total":
            records = load_records()
            total = sum(r["amount"] for r in records)
            self._set_headers(200)
            self.wfile.write(json.dumps({"total": total}).encode("utf-8"))
            return

        # カテゴリ別集計
        if parsed.path == "/records/summary":
            records = load_records()
            cat_sum = {}
            for r in records:
                cat = r["category"]
                cat_sum[cat] = cat_sum.get(cat, 0) + r["amount"]
            self._set_headers(200)
            self.wfile.write(json.dumps(cat_sum).encode("utf-8"))
            return

        else:
            # 未定義のパス → 404
            self._set_headers(404)
            self.wfile.write(json.dumps(
                {"eeror": "Not Found"}).encode("utf-8"))

    def do_POST(self):
        """
        POST /records を処理 — JSON ボディから新しい記録を追加
        期待する JSON フォーマット:
            { "date": "...", "category": "...", "amount": 123 }
        """
        parsed = urlparse(self.path)
        if parsed.path == "/records":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps(
                    {"error": "Invalid JSON"}).encode("utf-8"))
                return

            # 必須キーの存在チェック
            if not ("date" in data and "category" in data and "amount" in data):
                self._set_headers(400)
                self.wfile.write(json.dumps(
                    {"error": "missing fields"}).encode("utf-8"))
                return

            # ランダムな一意 ID を付与
            data["id"] = str(uuid.uuid4())

            records = load_records()
            records.append(data)
            save_records(records)

            self._set_headers(201)
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps(
                {"error": "Not Found"}).encode("utf-8"))

    def do_PUT(self):
        """
        PUT /records{id} を処理 — 指定 ID のデータを編集
        """
        parsed = urlparse(self.path)
        # 正しいルートか確認
        if parsed.path.startswith("/records/"):
            record_id = parsed.path.split("/")[-1]
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps(
                    {"error": "Invalid JSON"}).encode("utf-8")
                )
                return

            records = load_records()
            for r in records:
                if r.get("id") == record_id:
                    # 編集したい項目だけ更新
                    r.update(data)  # 値を上書き
                    save_records(records)
                    self._set_headers(200)
                    self.wfile.write(json.dumps(r).encode("utf-8"))
                    return

        else:
            # 指定 ID のレコードが見つからなかった場合
            self._set_headers(404)
            self.wfile.write(json.dumps(
                {"error": "Not Found"}).encode("utf-8"))

    def do_DELETE(self):
        """
        DELETE /records/{id} を処理 — 指定された ID のレコードを削除
        """
        parsed = urlparse(self.path)
        if parsed.path.startswith("/records/"):
            record_id = parsed.path.split("/")[-1]
            records = load_records()
            new_records = [r for r in records if r["id"] != record_id]
            save_records(new_records)
            self._set_headers(200)
            self.wfile.write(json.dumps(
                {"deleted": record_id}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps(
                {"error": "Not Found"}).encode("utf-8")
            )


def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):
    """サーバを起動する関数"""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server at http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
