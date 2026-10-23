"""AION Zero regression and safety tests. All data is created in temporary directories."""
import gzip
import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

APP = Path(__file__).resolve().parent / "aion.py"


class AionTests(unittest.TestCase):
    def run_cli(self, data_dir, *args, expected=0):
        env = os.environ.copy()
        env["AION_DATA_DIR"] = str(data_dir)
        result = subprocess.run([sys.executable, str(APP), *map(str, args)], capture_output=True,
                                text=True, env=env, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_init_add_search_persistence_and_compression(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            out = self.run_cli(data, "init")
            self.assertIn("Integrity: ok", out)
            body = "Before a deployment, run automated regression tests. " * 120
            out = self.run_cli(data, "add", "Deployment lesson", "--body", body, "--kind", "lesson", "--category", "devops")
            self.assertIn("record #1", out)
            out = self.run_cli(data, "search", "regression deployment")
            self.assertIn("Deployment lesson", out)
            out = self.run_cli(data, "show", "1")
            self.assertIn(body[:100], out)
            out = self.run_cli(data, "stats")
            self.assertIn("Compressed body savings:", out)
            self.assertIn("FTS5 metadata search:", out)

    def test_duplicate_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            self.run_cli(data, "add", "Same", "--body", "Unique durable lesson.", "--kind", "knowledge")
            out = self.run_cli(data, "add", "Different title", "--body", "Unique durable lesson.", "--kind", "knowledge")
            self.assertIn("duplicate: record #1", out)
            self.assertIn("Records: 1", self.run_cli(data, "stats"))

    def test_secret_rejected_and_searchable_record_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            out = self.run_cli(data, "add", "Bad sample", "--body", "-----BEGIN RSA PRIVATE KEY-----\nsecret",
                               expected=1)
            self.assertIn("NOT saved", out)
            self.assertIn("Records: 0", self.run_cli(data, "stats"))

    def test_verification_requires_evidence_and_correct_transition(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            self.run_cli(data, "add", "Fix procedure", "--body", "Restart the lab container and run the test.", "--kind", "procedure")
            out = self.run_cli(data, "verify", "1", "--status", "verified", "--evidence", "Looks good.", expected=1)
            self.assertIn("Only a 'tested' record", out)
            self.run_cli(data, "verify", "1", "--status", "tested", "--evidence", "Unit test passed on Python 3.12.")
            self.run_cli(data, "verify", "1", "--status", "verified", "--evidence", "Integration test passed on the stated lab version.", "--confidence", "0.95")
            out = self.run_cli(data, "show", "1")
            self.assertIn("verification_status: verified", out)
            self.assertIn("0.95", out)
            self.assertIn("Integration test passed", out)

    def test_task_journal_and_lesson_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            out = self.run_cli(data, "task", "start", "Fix container health check", "--objective", "Make local service health check pass", "--environment", "Linux lab", "--versions", "Docker 27", "--category", "devops")
            self.assertIn("Task #1", out)
            self.run_cli(data, "task", "update", "1", "--field", "hypotheses", "--value", "Container listens on a different port")
            self.run_cli(data, "task", "update", "1", "--field", "actions", "--value", "Inspected healthcheck config")
            out = self.run_cli(data, "task", "close", "1", "--outcome", "success", "--validation", "Health check passed in 3 consecutive runs", "--lesson", "Match health-check port to service port", "--solution", "Update the health-check port and retest")
            self.assertIn("lesson created as record #2", out)
            out = self.run_cli(data, "task", "show", "1")
            self.assertIn("Container listens on a different port", out)
            self.assertIn('"outcome": "success"', out)
            out = self.run_cli(data, "related", "1")
            self.assertIn("#2", out)
            self.assertIn("unverified", out)

    def test_feedback_persists_and_is_searchable(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            self.run_cli(data, "add", "Python script", "--body", "Use a temporary directory in unit tests.", "--kind", "knowledge")
            out = self.run_cli(data, "feedback", "1", "worked", "--lesson", "Temporary directory test passed.")
            self.assertIn("Feedback stored", out)
            out = self.run_cli(data, "search", "Temporary directory test")
            self.assertIn("Feedback on #1", out)

    def test_ingest_skips_secrets_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "notes"
            root.mkdir()
            (root / "good.md").write_text("Kubernetes readiness probes monitor application health.", encoding="utf-8")
            (root / "bad.txt").write_text("ghp_" + "A" * 35, encoding="utf-8")
            (root / ".env").write_text("nothing useful", encoding="utf-8")
            outside = Path(tmp) / "outside.md"
            outside.write_text("symlink target content", encoding="utf-8")
            try:
                (root / "link.md").symlink_to(outside)
            except (OSError, NotImplementedError):
                pass
            data = Path(tmp) / "db"
            out = self.run_cli(data, "ingest", root, "--max-files", "20", "--max-total-mib", "5")
            self.assertIn("Import summary", out)
            self.assertIn("good.md", out)
            self.assertIn("skipped", out)
            self.assertNotIn("ghp_", self.run_cli(data, "search", "ghp"))
            self.assertIn("readiness probes", self.run_cli(data, "search", "readiness probes"))

    def test_backup_restore_and_jsonl_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            self.run_cli(data, "add", "Memory A", "--body", "Backups preserve durable memory.", "--kind", "knowledge")
            backup = Path(tmp) / "backups" / "aion.sqlite3"
            out = self.run_cli(data, "backup", backup)
            self.assertIn("Integrity: ok", out)
            export = Path(tmp) / "memory.jsonl.gz"
            out = self.run_cli(data, "export", export, "--gzip")
            self.assertIn("Exported 1 records", out)
            with gzip.open(export, "rt", encoding="utf-8") as fh:
                obj = json.loads(fh.readline())
            self.assertEqual(obj["title"], "Memory A")
            self.run_cli(data, "add", "Memory B", "--body", "A second local record.", "--kind", "knowledge")
            no_confirm = self.run_cli(data, "restore", backup, expected=1)
            self.assertIn("Rerun with --yes", no_confirm)
            out = self.run_cli(data, "restore", backup, "--yes")
            self.assertIn("Restored and validated", out)
            self.assertIn("Memory A", self.run_cli(data, "search", "durable memory"))
            self.assertNotIn("Memory B", self.run_cli(data, "search", "second local record"))

    def test_path_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "normal.md"
            original.write_text("safe text", encoding="utf-8")
            link = root / "linked.md"
            try:
                link.symlink_to(original)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable on this platform")
            env = os.environ.copy()
            env["AION_DATA_DIR"] = str(root / "db")
            result = subprocess.run([sys.executable, str(APP), "add", "linked", "--file", str(link)],
                                    capture_output=True, text=True, env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symbolic link", result.stderr.lower())

    def test_doctor_and_memory_commands_do_not_attempt_network(self):
        # Load a separate module instance pointed at a temporary database and block all socket connections.
        with tempfile.TemporaryDirectory() as tmp:
            old_data_dir = os.environ.get("AION_DATA_DIR")
            os.environ["AION_DATA_DIR"] = str(Path(tmp) / "db")
            try:
                spec = importlib.util.spec_from_file_location("aion_offline_test", APP)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                def forbidden(*_args, **_kwargs):
                    raise AssertionError("Unexpected socket connection in offline core path")
                import contextlib
                import io
                with mock.patch.object(socket.socket, "connect", forbidden), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(mod.main(["doctor"]), 0)
                    self.assertEqual(mod.main(["add", "Offline", "--body", "Offline core persists this."]), 0)
                    self.assertEqual(mod.main(["search", "persists offline"]), 0)
            finally:
                if old_data_dir is None:
                    os.environ.pop("AION_DATA_DIR", None)
                else:
                    os.environ["AION_DATA_DIR"] = old_data_dir

    def test_migrates_older_starter_database_without_losing_records(self):
        import hashlib
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            data.mkdir()
            path = data / "aion.sqlite3"
            body = "Legacy memory must survive the schema migration."
            raw = body.encode("utf-8")
            packed = gzip.compress(raw, mtime=0)
            with sqlite3.connect(path) as conn:
                conn.execute("""CREATE TABLE records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, title TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general', tags TEXT NOT NULL DEFAULT '',
                    source TEXT NOT NULL DEFAULT 'manual', sha256 TEXT NOT NULL, body_gzip BLOB NOT NULL,
                    original_bytes INTEGER NOT NULL, compressed_bytes INTEGER NOT NULL,
                    summary TEXT NOT NULL DEFAULT '', outcome TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
                    UNIQUE(sha256, kind))""")
                conn.execute("INSERT INTO records(kind,title,category,tags,source,sha256,body_gzip,original_bytes,compressed_bytes,summary,outcome,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    ("knowledge", "Legacy note", "python", "migration", "manual", hashlib.sha256(raw).hexdigest(), packed, len(raw), len(packed), "old starter", "", "2026-01-01T00:00:00+00:00"))
            out = self.run_cli(data, "search", "legacy memory migration")
            self.assertIn("Legacy note", out)
            shown = self.run_cli(data, "show", "1")
            self.assertIn("verification_status: unverified", shown)
            self.assertIn(body, shown)
            with sqlite3.connect(path) as conn:
                self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 2)

    def test_revision_created_when_task_updated(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            self.run_cli(data, "task", "start", "Revision test", "--objective", "Check revisions")
            self.run_cli(data, "task", "update", "1", "--field", "actions", "--value", "First attempted action")
            # Verify the prior body was preserved in the revision store.
            import sqlite3
            with sqlite3.connect(data / "aion.sqlite3") as conn:
                count = conn.execute("SELECT COUNT(*) FROM record_revisions WHERE record_id=1").fetchone()[0]
            self.assertGreaterEqual(count, 1)
            history = self.run_cli(data, "history", "1")
            self.assertIn("Revision 1", history)

    def test_structured_procedure_starts_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            out = self.run_cli(data, "procedure", "add", "Restart local service", "--prerequisites", "Lab VM accessible", "--steps", "Restart service; inspect status", "--expected", "Service returns healthy", "--risks", "Brief outage", "--rollback", "Restore prior config", "--context", "Docker test lab")
            self.assertIn("status=unverified", out)
            shown = self.run_cli(data, "show", "1")
            self.assertIn('"prerequisites": "Lab VM accessible"', shown)
            self.assertIn("verification_status: unverified", shown)

    def test_verification_evidence_rejects_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "db"
            self.run_cli(data, "add", "Procedure", "--body", "Use a safe procedure.", "--kind", "procedure")
            out = self.run_cli(data, "verify", "1", "--status", "tested", "--evidence", "ghp_" + "B" * 35, expected=1)
            self.assertIn("Possible credential detected", out)
            shown = self.run_cli(data, "show", "1")
            self.assertIn("verification_status: unverified", shown)


if __name__ == "__main__":
    unittest.main(verbosity=2)
