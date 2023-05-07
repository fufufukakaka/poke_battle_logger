import glob
import os

from google.cloud import storage


class GCSHandler:
    def __init__(self) -> None:
        self.bucket_name = "poke_battle_logger_templates"
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(self.bucket_name)

    def upload_unknown_pokemon_templates_to_gcs(self, trainer_id: int) -> None:
        """
        target_gcs_path -> gcs://{bucket_name}/pokemon_templates/users/{trainer_id}/unknown_pokemon_templates/*.png

        upload 後、local のファイルを削除する
        """
        for path in glob.glob("template_images/unknown_pokemon_templates/*.png"):
            blob = self.bucket.blob(
                f"pokemon_templates/users/{trainer_id}/unknown_pokemon_templates/{path.split('/')[-1]}"
            )
            blob.upload_from_filename(path)
            # delete local file
            os.remove(path)

    def upload_unknown_pokemon_name_window_templates_to_gcs(self, trainer_id: int) -> None:
        """
        target_gcs_path -> gcs://{bucket_name}/pokemon_name_window_templates/users/{trainer_id}/unknown_pokemon_name_window_templates/*.png
        """
        for path in glob.glob("template_images/unknown_pokemon_name_window_templates/*.png"):
            blob = self.bucket.blob(
                f"pokemon_name_window_templates/users/{trainer_id}/unknown_pokemon_name_window_templates/{path.split('/')[-1]}"
            )
            blob.upload_from_filename(path)
            # delete local file
            os.remove(path)
