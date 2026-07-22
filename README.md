# 秋山翔吾 日米通算安打ページ

GitHub Pagesで公開するためのファイル一式です。

## 表示内容

- 秋山翔吾
- 日米通算安打数
- NPB公式ページの情報日付
- 「昨季までの固定値＋今季安打数」の内訳
- NPB公式成績ページへのリンク

## データ更新の仕組み

1. GitHub Actionsが毎日NPB公式成績ページを取得
2. `#tablefix_b`内の2026年行を探す
3. 7列目の「安打」を取得
4. `#p_common_smenu time`から情報日付を取得
5. `data.js`を更新
6. HTMLが`data.js`を読み込んで画面へ表示

昨季までの日米通算安打数は、`update_stats.py`の
`PREVIOUS_SEASON_HITS = 1832`で固定しています。

## GitHubでの公開手順

1. このフォルダ内のファイルをリポジトリのルートへ配置
2. GitHubのリポジトリで「Settings」を開く
3. 「Pages」を開く
4. 公開元をメインブランチのルートに設定
5. 「Actions」で`Update Akiyama hit count`を手動実行

以後は毎日、日本時間21:15ごろに更新処理が実行されます。

## ファイル

- `index.html`：表示ページ
- `data.js`：表示する成績データ
- `update_stats.py`：NPBページの取得・解析
- `requirements.txt`：Python依存パッケージ
- `.github/workflows/update-stats.yml`：自動更新設定

## 注意

NPB公式サイトのHTML構造が変更された場合は、
`update_stats.py`のセレクタや列位置を修正する必要があります。
