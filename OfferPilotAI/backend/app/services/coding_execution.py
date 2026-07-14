"""Live coding execution adapters."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import time

from app.domain.enums import CodeRunStatus, CodingLanguage


MAX_OUTPUT_CHARS = 20_000


@dataclass(frozen=True)
class CodeExecutionInput:
    """Code runner input."""

    language: CodingLanguage
    source_code: str
    stdin: str
    timeout_seconds: float


@dataclass(frozen=True)
class CodeExecutionResult:
    """Code runner output."""

    language: CodingLanguage
    status: CodeRunStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    execution_time_ms: int | None = None
    memory_kb: int | None = None


class CodeExecutionService:
    """Execute code using constrained local runners.

    This adapter avoids shells, uses temporary directories, applies timeouts, and adds
    lightweight static safety checks. Production deployments should still run this
    service inside an isolated worker container or firecracker-style sandbox.
    """

    blocked_python_imports = {
        "ctypes",
        "multiprocessing",
        "os",
        "pathlib",
        "resource",
        "shutil",
        "signal",
        "socket",
        "subprocess",
        "threading",
    }
    blocked_python_calls = {"eval", "exec", "compile", "__import__", "open", "input.__globals__"}
    blocked_java_patterns = (
        "Runtime.getRuntime",
        "ProcessBuilder",
        "java.io.File",
        "java.nio.file",
        "Socket",
        "System.exit",
    )
    blocked_sql_patterns = (
        "attach database",
        "load_extension",
        "pragma writable_schema",
        "create virtual table",
    )

    def __init__(self, *, execution_enabled: bool = True) -> None:
        self.execution_enabled = execution_enabled

    async def execute(self, payload: CodeExecutionInput) -> CodeExecutionResult:
        if not self.execution_enabled:
            return CodeExecutionResult(
                language=payload.language,
                status=CodeRunStatus.SKIPPED,
                stderr="Live code execution is disabled by configuration.",
            )

        safety_error = self._safety_error(payload)
        if safety_error:
            return CodeExecutionResult(language=payload.language, status=CodeRunStatus.FAILED, stderr=safety_error)

        if payload.language == CodingLanguage.PYTHON:
            return await self._execute_python(payload)
        if payload.language == CodingLanguage.JAVA:
            return await self._execute_java(payload)
        if payload.language == CodingLanguage.SQL:
            return await self._execute_sql(payload)

        return CodeExecutionResult(
            language=payload.language,
            status=CodeRunStatus.UNSUPPORTED,
            stderr=f"Language {payload.language} is not supported.",
        )

    def _safety_error(self, payload: CodeExecutionInput) -> str | None:
        if payload.language == CodingLanguage.PYTHON:
            return self._python_safety_error(payload.source_code)
        if payload.language == CodingLanguage.JAVA:
            for pattern in self.blocked_java_patterns:
                if pattern in payload.source_code:
                    return f"Potentially unsafe Java pattern detected: {pattern}."
        if payload.language == CodingLanguage.SQL:
            lowered = payload.source_code.lower()
            for pattern in self.blocked_sql_patterns:
                if pattern in lowered:
                    return f"Potentially unsafe SQL statement detected: {pattern}."
        return None

    def _python_safety_error(self, source_code: str) -> str | None:
        try:
            import ast

            tree = ast.parse(source_code)
        except SyntaxError:
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".", 1)[0]
                    if module_name in self.blocked_python_imports:
                        return f"Potentially unsafe Python import detected: {module_name}."
            if isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module.split(".", 1)[0]
                if module_name in self.blocked_python_imports:
                    return f"Potentially unsafe Python import detected: {module_name}."
            if isinstance(node, ast.Call):
                call_name = self._call_name(node.func)
                if call_name in self.blocked_python_calls:
                    return f"Potentially unsafe Python call detected: {call_name}."
        return None

    def _call_name(self, node: object) -> str:
        import ast

        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = self._call_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        return ""

    async def _execute_python(self, payload: CodeExecutionInput) -> CodeExecutionResult:
        with tempfile.TemporaryDirectory(prefix="offerpilot-ai-py-") as temp_dir:
            source_path = Path(temp_dir) / "solution.py"
            source_path.write_text(payload.source_code, encoding="utf-8")
            return await self._run_process(
                [sys.executable, "-I", str(source_path)],
                cwd=temp_dir,
                stdin=payload.stdin,
                timeout_seconds=payload.timeout_seconds,
            )

    async def _execute_java(self, payload: CodeExecutionInput) -> CodeExecutionResult:
        javac_path = shutil.which("javac")
        java_path = shutil.which("java")
        if not javac_path or not java_path:
            return CodeExecutionResult(
                language=payload.language,
                status=CodeRunStatus.UNSUPPORTED,
                stderr="Java runtime is not available on this worker.",
            )
        if "class Main" not in payload.source_code:
            return CodeExecutionResult(
                language=payload.language,
                status=CodeRunStatus.FAILED,
                stderr="Java submissions must include a public or package-private Main class.",
            )

        with tempfile.TemporaryDirectory(prefix="offerpilot-ai-java-") as temp_dir:
            source_path = Path(temp_dir) / "Main.java"
            source_path.write_text(payload.source_code, encoding="utf-8")
            compile_result = await self._run_process(
                [javac_path, str(source_path)],
                cwd=temp_dir,
                stdin="",
                timeout_seconds=payload.timeout_seconds,
                language=payload.language,
            )
            if compile_result.status != CodeRunStatus.SUCCESS:
                return compile_result
            run_result = await self._run_process(
                [java_path, "-Xmx128m", "-cp", temp_dir, "Main"],
                cwd=temp_dir,
                stdin=payload.stdin,
                timeout_seconds=payload.timeout_seconds,
                language=payload.language,
            )
            return run_result

    async def _execute_sql(self, payload: CodeExecutionInput) -> CodeExecutionResult:
        start = time.perf_counter()
        try:
            stdout = await asyncio.wait_for(
                asyncio.to_thread(self._execute_sql_sync, payload.source_code),
                timeout=payload.timeout_seconds,
            )
            return CodeExecutionResult(
                language=payload.language,
                status=CodeRunStatus.SUCCESS,
                stdout=stdout,
                exit_code=0,
                execution_time_ms=self._elapsed_ms(start),
            )
        except TimeoutError:
            return CodeExecutionResult(
                language=payload.language,
                status=CodeRunStatus.TIMEOUT,
                stderr=f"SQL execution exceeded {payload.timeout_seconds:.1f}s timeout.",
                execution_time_ms=self._elapsed_ms(start),
            )
        except sqlite3.Error as exc:
            return CodeExecutionResult(
                language=payload.language,
                status=CodeRunStatus.FAILED,
                stderr=str(exc),
                exit_code=1,
                execution_time_ms=self._elapsed_ms(start),
            )

    def _execute_sql_sync(self, source_code: str) -> str:
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        outputs: list[dict[str, object]] = []
        try:
            for statement in self._split_sql_statements(source_code):
                cursor = connection.execute(statement)
                if cursor.description:
                    columns = [description[0] for description in cursor.description]
                    rows = [dict(row) for row in cursor.fetchmany(100)]
                    outputs.append({"columns": columns, "rows": rows, "row_count": len(rows)})
            connection.commit()
        finally:
            connection.close()

        if not outputs:
            return "SQL executed successfully."
        return self._clip(json.dumps(outputs, indent=2, default=str))

    def _split_sql_statements(self, source_code: str) -> list[str]:
        statements: list[str] = []
        buffer: list[str] = []
        for line in source_code.splitlines():
            buffer.append(line)
            candidate = "\n".join(buffer).strip()
            if sqlite3.complete_statement(candidate):
                statements.append(candidate)
                buffer = []
        trailing = "\n".join(buffer).strip()
        if trailing:
            statements.append(trailing)
        return statements

    async def _run_process(
        self,
        command: Sequence[str],
        *,
        cwd: str,
        stdin: str,
        timeout_seconds: float,
        language: CodingLanguage = CodingLanguage.PYTHON,
    ) -> CodeExecutionResult:
        start = time.perf_counter()
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            env=self._process_env(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=self._limit_process_resources if os.name == "posix" else None,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(stdin.encode("utf-8")),
                timeout=timeout_seconds,
            )
        except TimeoutError:
            process.kill()
            await process.wait()
            return CodeExecutionResult(
                language=language,
                status=CodeRunStatus.TIMEOUT,
                stderr=f"Execution exceeded {timeout_seconds:.1f}s timeout.",
                execution_time_ms=self._elapsed_ms(start),
            )

        stdout = self._clip(stdout_bytes.decode("utf-8", errors="replace"))
        stderr = self._clip(stderr_bytes.decode("utf-8", errors="replace"))
        return CodeExecutionResult(
            language=language,
            status=CodeRunStatus.SUCCESS if process.returncode == 0 else CodeRunStatus.FAILED,
            stdout=stdout,
            stderr=stderr,
            exit_code=process.returncode,
            execution_time_ms=self._elapsed_ms(start),
        )

    def _process_env(self) -> dict[str, str]:
        return {
            "PATH": os.environ.get("PATH", ""),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONIOENCODING": "utf-8",
        }

    def _limit_process_resources(self) -> None:
        try:
            import resource

            resource.setrlimit(resource.RLIMIT_CPU, (3, 4))
            resource.setrlimit(resource.RLIMIT_FSIZE, (1_000_000, 1_000_000))
            resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
            if hasattr(resource, "RLIMIT_AS"):
                resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
        except Exception:
            return

    def _elapsed_ms(self, start: float) -> int:
        return max(0, int((time.perf_counter() - start) * 1000))

    def _clip(self, value: str) -> str:
        if len(value) <= MAX_OUTPUT_CHARS:
            return value
        return value[:MAX_OUTPUT_CHARS] + "\n...[output truncated]"
