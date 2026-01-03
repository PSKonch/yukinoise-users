from typing import BinaryIO
from minio import Minio
from minio.commonconfig import CopySource


class MinioStorageClient:
    def __init__(
        self, endpoint_url: str, access_key: str, secret_key: str, bucket_name: str
    ):
        self._client = Minio(
            endpoint=endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
        )
        self._bucket_name = bucket_name

    async def get_file_url(self, bucket: str, file_key: str) -> bytes:
        file = await self._client.get_object(bucket, file_key)
        data = await file.read()
        from typing import cast

        return cast(bytes, data)

    async def upload_file(
        self, file_key: str, bucket: str, stream: BinaryIO, part_size: int
    ) -> None:
        await self._client.put_object(
            bucket_name=bucket,
            object_name=file_key,
            data=stream,
            length=-1,
            part_size=part_size,
        )

    async def delete_file(self, bucket: str, file_key: str) -> None:
        await self._client.remove_object(bucket, file_key)

    async def delete_batch_files(self, bucket: str, file_keys: list[str]) -> None:
        objects_to_delete = [file_key for file_key in file_keys]
        await self._client.remove_objects(bucket, objects_to_delete)

    async def move_file(self, bucket: str, source_key: str, dest_key: str) -> None:
        await self._client.copy_object(
            bucket_name=bucket,
            object_name=dest_key,
            source=CopySource(bucket, source_key),
        )
        await self.delete_file(bucket, source_key)

    async def is_file(self, bucket: str, file_key: str) -> bool:
        try:
            await self._client.stat_object(bucket, file_key)
            return True
        except Exception:
            return False

    async def list_files(self, bucket: str, prefix: str) -> list[str]:
        objects = await self._client.list_objects(bucket, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]

    async def close(self) -> None:
        await self._client.close()
