# PokeBattleLogger

![app](docs/app.png)

ポケモンSV のランクマッチ(マスターボール以上) の youtube 配信から、対戦データを抽出します。

🚧 This app is Under Construction 🚧

現在開発中です。

## Notification

- 対応環境(2023/03/06 時点)
  - 言語選択が英語の場合のみに対応しています。
  - 動画のサイズは 720p: 1280 x 720 (HD) のみに対応しています。
- 必ず「続ける」or「対戦チームを変える」で順位を表示する必要があります。表示されていない場合、正常に動作しません。
- また、バトルスタジアムから抜ける場合は動画を切って頂く必要があります。
- 何らかの理由で順位が変動しなかった試合についてはデータ抽出を行いません。

## Setup

Pyton 3.10 +

```
poetry install
```

## Batch

Tesseract を用いるので、環境変数を設定する必要があります。Makefile に設定されているので、自分の環境に合わせて調整してください。

```
make extract-data VIDEO_ID={your_pokemon_sv_rank_match_stream_id}
```

抽出したデータは sqlite に保存されます。

### For Unknown Pokemon Image

`make extract-data` を実行した際、次のようなエラーが出ることがあります。

```
Exception: Unknown pokemon exists. Stop processing. Please annotate unknown pokemons.
```

この場合、 `template_images/unknown_pokemon_templates` を見ると、検出に失敗したポケモンの画像が収録されているかと思います。
これを各ポケモンごとに最低1枚、{正しいポケモン名}.png に画像ファイル名を変更して、`template_images/labeled_pokemon_templates` に移動させてください。
同じ名前のファイルが既にある場合は、{正しいポケモン名}_{任意の番号}.png という名前にして被らないようにしてから移動させてください。

その後、 `make build-pokemon-faiss-index` を実行することで、次回のバッチからは反映されるようになります。再度 `make extract-data` を実行してください。

## Visualize App

```
make run-dashboard
```

### API

```
poetry run uvicorn poke_battle_logger.api.app:app
```
