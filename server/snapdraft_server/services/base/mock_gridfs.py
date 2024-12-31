import os
from dataclasses import dataclass, field
from pathlib import Path

from snapdraft_server.services.file_model import StoredFile


@dataclass
class MockFile:
    filename: str
    metadata: dict


@dataclass
class MockAsyncIOMotorGridFSBucket:
    dir: Path
    next_id: int = 0
    files: dict[str, MockFile] = field(default_factory=dict)

    def __call__(self, *args, **kwargs):
        return self

    def __post_init__(self):
        os.makedirs(self.dir, exist_ok=True)

    async def upload_from_stream(self, filename: str, source: any, metadata: dict):
        id = hex(self.next_id)[2:].zfill(24)
        self.next_id += 1
        self.files[id] = MockFile(filename, metadata)
        with open(self.dir / f"{id}", "wb") as f:
            f.write(source.read())
        return id
