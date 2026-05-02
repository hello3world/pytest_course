from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional


class StorageBackend(ABC):
    """Abstract persistent backend storage.

    This base class is capable of enforcing a single in-process owner via :meth:`reserve`
    and an explicit lifecycle via :meth:`close`. Subclasses should implement
    :meth:`save`, :meth:`load`, and the storage-specific :meth:`_close`.

    Important:
        Backends may hold system resources (e.g., file locks or open connections to DB). Always call
        :meth:`close` when finished or, preferably, use a context manager to
        ensure proper release:
    """

    def __init__(self) -> None:
        self._owner: Optional[object] = None
        self._closed = False

    # ------------------------- Persistence API ---------------------------------
    @abstractmethod
    def _save(self, payload: Dict[str, Any]) -> None:
        """Persist the given payload to the backend."""
        pass

    @abstractmethod
    def _load(self) -> Dict[str, Any]:
        """Retrieve and return the latest payload from the backend."""
        pass

    @abstractmethod
    def _close(self) -> None:
        """Storage-specific logic for closing the backend (internal)."""
        pass

    def save(self, *args, **kwargs) -> None:
        self._ensure_open()
        self._save(*args, **kwargs)

    def load(self) -> Dict[str, Any]:
        self._ensure_open()
        return self._load()

    def _ensure_open(self) -> None:
        """Raise if the storage has been closed (internal)."""
        if self._closed:
            raise RuntimeError("Storage is closed. Create a new storage or use a context manager.")

    # ------------------------- Lifecycle Management ---------------------------------

    def close(self) -> None:
        """Release all storage resources.

        This method finalizes the storage lifecycle by releasing any resources
        held by the backend (such as file handles, database connections, or
        locks). Once closed, the backend instance becomes unusable — any further
        calls to :meth:`save`, :meth:`load`, or :meth:`reserve` are invalid.
        Create a new instance if continued use is required.

        Notes:
            - Safe to call multiple times (subsequent calls have no effect).
            - The current owner (if any) is cleared to avoid accidental reuse
              after closure.
            - Prefer using the backend as a context manager (``with`` statement),
              which guarantees that :meth:`close` is invoked automatically.
        """
        if self._closed:
            return
        self._close()
        self._closed = True
        self._owner = None

    def __enter__(self):
        """Enter a context manager and return ``self``."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Exit the context manager and close the backend."""
        self.close()

    # ------------------------- Ownership Control ---------------------------------
    def reserve(self, owner: object) -> bool:
        """Claim exclusive ownership of this backend instance.

        This method enforces a *single in-process owner* rule. Once reserved,
        the backend may only be used by the reserving object until explicitly
        released (via :meth:`_release`) or closed (via :meth:`close`).

        Args:
            owner: An arbitrary object used to identify the caller that claims
                ownership of this storage instance.

        Raises:
            RuntimeError: If the backend has already been closed.
            RuntimeError: If the backend is already reserved by another owner.

        Notes:
            - Only one owner may hold the reservation at a time.
            - Ownership is cleared automatically when :meth:`close` is called.
            - Typical usage is to call :meth:`reserve` once after construction,
              before performing any :meth:`save` or :meth:`load` operations.
            - Intended for in-process coordination only (not a cross-process
              lock or synchronization primitive).
        """
        if self._closed:
            raise RuntimeError("Cannot reserve a closed storage.")
        if self._owner is None:
            self._owner = owner
            return True
        raise RuntimeError("This storage instance is already in use by another owner.")

    def _release(self, owner: object) -> None:
        """Release the reservation if held by the given owner (internal)."""
        if self._owner is owner:
            self._owner = None


class JsonFileStorage(StorageBackend):
    """File-based storage with a process-level lock and atomic writes.

    Features:
      - Exclusive sidecar lock file to prevent concurrent use across processes.
      - Atomic writes via temp-file + replace.
      - Explicit :meth:`close` required to release the lock (or use a ``with`` block).

    Args:
        path: Path to the JSON file that stores the payload.
        lockfile: Optional explicit path to the lock file. Defaults to
            ``<path>.lock``.

    Examples:
        Using a context manager (recommended):

        >>> from pathlib import Path
        >>> with JsonFileStorage(Path("/tmp/state.json")) as storage:
        ...     storage.save({"a": 1})
        ...     storage.load()
        {'a': 1}

        Manual close:

        >>> storage = JsonFileStorage(Path("/tmp/state.json"))
        >>> try:
        ...     storage.save({"ok": True})
        ...     storage.load()
        ... finally:
        ...     storage.close()
    """

    def __init__(self, path: Path, lockfile: Optional[Path] = None) -> None:
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._lock_path = Path(lockfile) if lockfile else self.path.with_suffix(self.path.suffix + ".lock")
        self._lock_fd: Optional[int] = None

        self._acquire_lock()

    def _save(self, payload: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(payload, ensure_ascii=False, indent=2)

        # Atomic write: write to a temp file in the same directory then replace
        with NamedTemporaryFile("w", delete=False, dir=self.path.parent, encoding="utf-8") as tf:
            tmp_name = tf.name
            tf.write(data)
            tf.flush()
            os.fsync(tf.fileno())
        os.replace(tmp_name, self.path)

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        text = self.path.read_text(encoding="utf-8")
        return json.loads(text) if text else {}

    def _close(self) -> None:
        self._release_lock()

    def _acquire_lock(self) -> None:
        """Create and hold an exclusive lockfile (internal)."""
        flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
        try:
            self._lock_fd = os.open(self._lock_path, flags, 0o600)
            os.write(self._lock_fd, str(os.getpid()).encode("ascii"))
            os.fsync(self._lock_fd)
        except FileExistsError as e:
            raise RuntimeError(
                f"Storage lock already held: {self._lock_path}. "
                f"Another process/test likely uses this storage."
            ) from e

    def _release_lock(self) -> None:
        """Close and remove the lockfile if held (internal)."""
        try:
            if self._lock_fd is not None:
                os.close(self._lock_fd)
                self._lock_fd = None
        finally:
            try:
                if self._lock_path.exists():
                    self._lock_path.unlink()
            except FileNotFoundError:
                pass
