import glob
import os
from typing import List, cast

from google.cloud import storage  # type: ignore
from tenacity import retry, stop_after_attempt

from poke_battle_logger.types import ImageLabel, NameWindowImageLabel


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

    def download_pokemon_name_window_templates(self, trainer_id: int) -> None:
        source_folder_prefix = f"pokemon_name_window_templates/users/{trainer_id}/labeled_pokemon_name_window_templates/"
        destination_folder_prefix = (
            "template_images/user_labeled_pokemon_name_window_templates/"
        )

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

    @retry(stop=stop_after_attempt(5))
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

    @retry(stop=stop_after_attempt(5))
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

    def set_label_unknown_pokemon_images(
        self, trainer_id_in_DB: int, image_labels: List[ImageLabel]
    ) -> None:
        for image_label in image_labels:
            # Create the destination directory
            dest_dir = f"pokemon_templates/users/{trainer_id_in_DB}/labeled_pokemon_templates/{image_label.pokemon_label}"
            dest_path = (
                f"{dest_dir}/{os.path.basename(image_label.pokemon_image_file_on_gcs)}"
            )

            # Move the file
            self._move_file(image_label.pokemon_image_file_on_gcs, dest_path)

    def set_label_unknown_pokemon_name_window_images(
        self, trainer_id_in_DB: int, image_labels: List[NameWindowImageLabel]
    ) -> None:
        for image_label in image_labels:
            # Create the destination directory
            dest_dir = f"pokemon_name_window_templates/users/{trainer_id_in_DB}/labeled_pokemon_name_window_templates/{image_label.pokemon_name_window_label}"
            dest_path = f"{dest_dir}/{os.path.basename(image_label.pokemon_name_window_image_file_on_gcs)}"

            # Move the file
            self._move_file(
                image_label.pokemon_name_window_image_file_on_gcs, dest_path
            )

    def check_user_battle_video_exists(
        self, trainer_id_in_DB: int, video_id: str
    ) -> bool:
        source_path = f"user_battle_video/{trainer_id_in_DB}/{video_id}.mp4"
        blob = self.bucket.blob(source_path)
        _is_exist = cast(bool, blob.exists())
        return _is_exist

    def download_video_from_gcs(
        self, trainer_id_in_DB: int, video_id: str, local_path: str
    ) -> None:
        source_path = f"user_battle_video/{trainer_id_in_DB}/{video_id}.mp4"
        blob = self.bucket.blob(source_path)
        blob.download_to_filename(local_path)

    def upload_video_to_gcs(
        self, trainer_id_in_DB: int, video_id: str, local_path: str
    ) -> None:
        dest_path = f"user_battle_video/{trainer_id_in_DB}/{video_id}.mp4"
        blob = self.bucket.blob(dest_path)
        blob.upload_from_filename(local_path)
