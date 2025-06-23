#!/bin/bash

# template_images/user_labeled_pokemon_templates 以下のディレクトリをループ
for pokemon_dir in template_images/user_labeled_pokemon_templates/*; do
  # ディレクトリ名を取得
  pokemon_name=$(basename "$pokemon_dir")
  
  # 対応するexperimentalディレクトリ
  target_dir="experimental/imgs/$pokemon_name"
  
  # ファイルを移動
  cp -r "$pokemon_dir" "$target_dir"
done
