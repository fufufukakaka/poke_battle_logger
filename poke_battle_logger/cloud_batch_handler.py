import os
from datetime import datetime

from google.cloud import batch_v1


class CloudBatchHandler:
    def __init__(self):
        # プロジェクト ID とロケーションを設定します。
        self.project_id = "turing-alcove-157907"
        self.location = "asia-northeast1"

    def submit_batch_job(self, job_name: str, task_groups: batch_v1.TaskGroup) -> None:
        # Batch サービスオブジェクトを作成します。
        batch_service = batch_v1.BatchServiceClient()

        # ジョブ コンフィグを作成します。
        batch_job_config = batch_v1.BatchJobConfig(
            project_id=self.project_id,
            location=self.location,
            job_name=job_name,
            task_groups=task_groups,
        )

        # ジョブを送信します。
        batch_service.projects().locations().jobs().create(
            name="projects/{}/locations/{}".format(batch_job_config.project_id, batch_job_config.location),
            body=batch_job_config.to_dict(),
        ).execute()

    def run_extract_stats_from_video_batch(self, video_id: str, trainer_id: str, language: str) -> None:
        # job_name postfix: timestamp
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        job_name = f"poke-battle-logger-job-{trainer_id}-{video_id}-{language}-{current_time}"

        # タスク グループを設定します。
        task_groups = [
            batch_v1.TaskGroup(
                task_count=1,
                parallelism=1,
                task_spec=batch_v1.TaskSpec(
                    compute_resource=batch_v1.ComputeResource(cpu_milli="4000", memory_mib="16384"),
                    runnables=[
                        batch_v1.Runnable(
                            container=batch_v1.Container(
                                image_uri="asia-northeast1-docker.pkg.dev/turing-alcove-157907/poke-battle-logger-job-api/production-image:latest",
                                entrypoint="",
                                commands=[
                                    "poetry",
                                    "run",
                                    "python",
                                    "scripts/run_extractor.py",
                                    "--trainer_id",
                                    trainer_id,
                                    "--video_id",
                                    video_id,
                                    "--language",
                                    language
                                ],
                                volumes=[],
                            ),
                            environment={
                                "ENV": os.environ["ENV"],
                                "HF_ACCESS_TOKEN": os.environ["HF_ACCESS_TOKEN"],
                                "POSTGRES_DB": os.environ["POSTGRES_DB"],
                                "POSTGRES_PASSWORD": os.environ["POSTGRES_PASSWORD"],
                                "POSTGRES_USER": os.environ["POSTGRES_USER"],
                                "POSTGRES_HOST": os.environ["POSTGRES_HOST"],
                                "POSTGRES_PORT": os.environ["POSTGRES_PORT"],
                                "RESEND_API_KEY": os.environ["RESEND_API_KEY"],
                            },
                        )
                    ],
                    volumes=[],
                ),
            ),
        ]

        self.submit_batch_job(job_name, task_groups)
