1.ユーザーが React で「記録を追加」や「一覧を取得」をクリック
2.React → HTTP POST／GET で Python サーバ にリクエスト送信
3.Python サーバ が JSON を受け取り／返し、データを読み書き
4.データは JSONファイル (records.json) に保存／読み込み
5.React は受け取った JSON を使って画面更新
