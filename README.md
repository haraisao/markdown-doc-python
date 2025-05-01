# GenMarkdown
## このパッケージについて
このパッケージは、PythonのプログラムからMarkdown形式の簡易マニュアルを生成することを目的にしています。

ソースコードを解析し、各クラス定義と関数定義の部分を抽出して、定義文の上に記載したコメントを説明だと仮定して作成しています。(コメントは、"#"が連続した部分を使用しています。)

実行するとmermaidのClassDiagramも生成しますが、現在のところファイル単位のツリーのみに対応しています。

また、簡単なプレビューのサーバープログラム(previewer.py)も作成しています。


また、ROSの実行中のノード構成などもドキュメント化したい場合には、[ros_to_markdown](https://github.com/RobRoyce/ros_to_markdown)を使うと便利です。

## プログラムと必要なツール
このパケージには、以下の2つのプログラムがあります。

- genPythonMd.py　　（ドキュメント生成）
- previewer.py （簡易プレビュー）

また、このパッケージは、以下のライブラリを使用しています。

- [ast-comments](https://pypi.org/project/ast-comments/)
- [Flask](https://pypi.org/project/Flask/)
- [Markdown](https://pypi.org/project/Markdown/)
- [markdown-include](https://pypi.org/project/markdown-include/)
- [markdown-mermaidjs](https://pypi.org/project/markdown-mermaidjs/)

これらのライブラリは、PyPIからダウンロードすることができますので、pipコマンドでインストールしてください。

## 使用方法

### マークダウンドキュメントの生成
ソースコードからマークダウンドキュメントを生成するには、以下のように実行します。

```
$ python3 genPythonMd.py <filename>
```

このコマンドを実行すると実行したディレクトリに **contents**というディレクトリを生成し、その下にMarkdownファイルを生成します。

### マークダウンファイルのプレビュー
生成したマークダウンファイルを見るために、簡易なHTTPサーバを作成しています。
このサーバーは、Flaskを使って実装しており、単独でも、uWSGI経由でも動作させることができます。

起動するには、以下のコマンドを実行して下さい。

```
$ python3 previewer.py
```

サーバープログラムの実行後、Webブラウザから http://localost:8080 にアクセスすることで contentsの下にあるマークダウンファイルをプレビューすることができます。

