import os
from datetime import datetime

from google.cloud import batch_v1


class CloudBatchHandler:
    def __init__(self) -> None:
        # プロジェクト ID とロケーションを設定します。
        self.project_id = "turing-alcove-157907"
        self.location = "asia-northeast1"

    def submit_batch_job(
        self, job_name: str, task_groups: list[batch_v1.TaskGroup]
    ) -> None:
        # Batch サービスオブジェクトを作成します。
        batch_service = batch_v1.BatchServiceClient()

        # インスタンスポリシー（利用する GCE インスタンス）を定義
        # https://cloud.google.com/python/docs/reference/batch/latest/google.cloud.batch_v1.types.AllocationPolicy.InstancePolicy
        policy = batch_v1.AllocationPolicy.InstancePolicy()
        policy.machine_type = "e2-standard-4"
        policy.provisioning_model = batch_v1.AllocationPolicy.ProvisioningModel.SPOT  # type: ignore

        # インスタンスポリシーの利用を宣言
        # https://cloud.google.com/python/docs/reference/batch/latest/google.cloud.batch_v1.types.AllocationPolicy.InstancePolicyOrTemplate
        instances = batch_v1.AllocationPolicy.InstancePolicyOrTemplate()
        instances.policy = policy

        # アロケーション・ポリシーを定義
        # https://cloud.google.com/python/docs/reference/batch/latest/google.cloud.batch_v1.types.AllocationPolicy
        allocation_policy = batch_v1.AllocationPolicy()
        allocation_policy.location = batch_v1.AllocationPolicy.LocationPolicy(
            allowed_locations=[
                "zones/asia-northeast1-a",
                "zones/asia-northeast1-b",
                "zones/asia-northeast1-c",
            ]
        )
        allocation_policy.instances = [instances]
        allocation_policy.service_account = batch_v1.ServiceAccount(
            email="poke-battle-logger@turing-alcove-157907.iam.gserviceaccount.com",
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/devstorage.full_control"
            ]
        )

        # 作成するジョブを定義
        # https://cloud.google.com/python/docs/reference/batch/latest/google.cloud.batch_v1.types.Job
        job = batch_v1.Job()
        job.task_groups = task_groups
        job.allocation_policy = allocation_policy
        job.logs_policy = batch_v1.LogsPolicy()
        job.logs_policy.destination = batch_v1.LogsPolicy.Destination.CLOUD_LOGGING  # type: ignore

        # ジョブを実行
        # https://cloud.google.com/python/docs/reference/batch/latest/google.cloud.batch_v1.services.batch_service.BatchServiceClient#google_cloud_batch_v1_services_batch_service_BatchServiceClient_create_job
        create_request = batch_v1.CreateJobRequest()
        create_request.job = job
        create_request.job_id = job_name
        create_request.parent = f"projects/{self.project_id}/locations/{self.location}"
        batch_service.create_job(create_request)

    def run_extract_stats_from_video_batch(
        self, video_id: str, trainer_id: str, language: str, finalResult: int | None
    ) -> None:
        if finalResult is None:
            commands = [
                "poetry",
                "run",
                "python",
                "scripts/run_extractor.py",
                "--trainer_id",
                trainer_id,
                "--video_id",
                video_id,
                "--language",
                language,
            ]
        else:
            commands = [
                "poetry",
                "run",
                "python",
                "scripts/run_extractor.py",
                "--trainer_id",
                trainer_id,
                "--video_id",
                video_id,
                "--language",
                language,
                "--finalResult",
                finalResult
            ]

        # job_name postfix: timestamp
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        job_name = f"poke-battle-logger-job-{current_time}"

        # task_groups
        environment = batch_v1.Environment()
        environment.variables = {
            "ENV": os.environ["ENV"],
            "HF_ACCESS_TOKEN": os.environ["HF_ACCESS_TOKEN"],
            "POSTGRES_DB": os.environ["POSTGRES_DB"],
            "POSTGRES_PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "POSTGRES_USER": os.environ["POSTGRES_USER"],
            "POSTGRES_HOST": os.environ["POSTGRES_HOST"],
            "POSTGRES_PORT": os.environ["POSTGRES_PORT"],
            "RESEND_API_KEY": os.environ["RESEND_API_KEY"],
        }

        task_groups = [
            batch_v1.TaskGroup(
                task_count=1,
                parallelism=1,
                task_spec=batch_v1.TaskSpec(
                    compute_resource=batch_v1.ComputeResource(
                        cpu_milli="4000", memory_mib="16384"
                    ),
                    runnables=[
                        batch_v1.Runnable(
                            container=batch_v1.Runnable.Container(
                                image_uri="asia-northeast1-docker.pkg.dev/turing-alcove-157907/poke-battle-logger-job-api/production-image:3077b915169318b431ab91d14aea8fcad673b3db",
                                entrypoint="",
                                commands=commands,
                                volumes=[],
                            )
                        )
                    ],
                    volumes=[],
                ),
                task_environments=[environment],
            ),
        ]

        self.submit_batch_job(job_name, task_groups)
