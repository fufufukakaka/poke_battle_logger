import glob
import os
import shutil
import unicodedata

import pandas as pd


def main():
    """
    ファイルをコピーする
    対象ファイル: template_images/labeled_pokemon_templates/{ポケモン名}_{meta}.png
    コピー先: experimental/imgs/{ポケモン名をid化したもの}/{1から始まる連番}.png

    ポケモン名について出現した順番に 0から連番で id を振り直し、その結果を id2name.csv に保存する
    experimental/imgs/{ポケモン名をid化したもの} が存在しない場合、そのフォルダを作成する

    また、あるポケモンに関する画像が 1枚しかない場合コピーして 2枚にする
    """
    pokemon_names = set()
    for path in glob.glob("template_images/labeled_pokemon_templates/*"):
        pokemon_name = path.split("/")[-1].split(".")[0].split("_")[0]
        pokemon_names.add(unicodedata.normalize("NFC", pokemon_name))
    pokemon_names = list(pokemon_names)
    pokemon_names.sort()

    df = pd.DataFrame({"id": range(len(pokemon_names)), "name": pokemon_names})
    df.to_csv("experimental/id2name.csv", index=False)

    for pokemon_name in pokemon_names:
        pokemon_name = unicodedata.normalize("NFC", pokemon_name)
        target_paths = glob.glob(
            f"template_images/labeled_pokemon_templates/{pokemon_name}*"
        )
        for i, path in enumerate(target_paths):
            if not glob.glob(f"experimental/imgs/{pokemon_name}"):
                os.mkdir(f"experimental/imgs/{pokemon_name}")
            shutil.copy(path, f"experimental/imgs/{pokemon_name}/{i}.png")
            if len(target_paths) == 1:
                shutil.copy(path, f"experimental/imgs/{pokemon_name}/{i + 1}.png")


if __name__ == "__main__":
    main()
