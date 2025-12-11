import unittest
import os
import json
from server import load_records, save_records, DATA_FILE


class TestRecords(unittest.TestCase):
    def setUp(self):
        # テスト用ファイル名を変更するか、既存ファイルをバックアップ
        if os.path.exists(DATA_FILE):
            os.rename(DATA_FILE, DATA_FILE + ".bak")

    def tearDown(self):
        # テスト終了後、テスト用ファイルを消す & バックアップを戻す
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        if os.path.exists(DATA_FILE + ".bak"):
            os.rename(DATA_FILE + ".bak", DATA_FILE)

    def test_load_empty(self):
        # ファイルがなければ、空リスト
        rec = load_records()
        self.assertEqual(rec, [])
