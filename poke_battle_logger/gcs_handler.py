import glob
import os
from typing import List

from google.cloud import storage

from poke_battle_logger.types import ImageLabel


class GCSHandler:
    def __init__(self) -> None:
        self.bucket_name = "poke_battle_logger_templates"
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(self.bucket_name)

    def download_pokemon_templates(self, trainer_id: int) -> None:
        source_folder_prefix = (
            f"pokemon_templates/users/{trainer_id}/labeled_pokemon_templates/"
        )
        destination_folder_prefix = "template_images/user_labeled_pokemon_templates/"

        # List all the folders in the source folder
        blobs = self.bucket.list_blobs(prefix=source_folder_prefix)

        # Download each file and save it to the local destination folder
        for blob in blobs:
            if blob.name.endswith("/"):
                continue

            source_path_parts = blob.name.split("/")
            pokemon_name = source_path_parts[-2]
            file_name = source_path_parts[-1]

            destination_folder = os.path.join(destination_folder_prefix, pokemon_name)
            os.makedirs(destination_folder, exist_ok=True)

            local_path = os.path.join(destination_folder, file_name)
            blob.download_to_filename(local_path)

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

    def upload_unknown_pokemon_name_window_templates_to_gcs(
        self, trainer_id: int
    ) -> None:
        """
        target_gcs_path -> gcs://{bucket_name}/pokemon_name_window_templates/users/{trainer_id}/unknown_pokemon_name_window_templates/*.png
        """
        for path in glob.glob(
            "template_images/unknown_pokemon_name_window_templates/*.png"
        ):
            blob = self.bucket.blob(
                f"pokemon_name_window_templates/users/{trainer_id}/unknown_pokemon_name_window_templates/{path.split('/')[-1]}"
            )
            blob.upload_from_filename(path)
            # delete local file
            os.remove(path)

    def _move_file(self, src_path: str, dest_path: str) -> None:
        source_blob = self.bucket.blob(src_path)
        _ = self.bucket.copy_blob(source_blob, self.bucket, dest_path)
        source_blob.delete()

    def set_label_unknown_pokemon_images(self, image_labels: List[ImageLabel]) -> None:
        for image_label in image_labels:
            # Create the destination directory
            dest_dir = f"pokemon_templates/users/1/labeled_pokemon_templates/{image_label.pokemon_label}"
            dest_path = (
                f"{dest_dir}/{os.path.basename(image_label.pokemon_image_file_on_gcs)}"
            )

            # Move the file
            self._move_file(image_label.pokemon_image_file_on_gcs, dest_path)
