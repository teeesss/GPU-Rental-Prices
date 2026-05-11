import logging
import os
from pathlib import Path
import paramiko
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("remote_sync")

ROOT = Path(__file__).parent.parent

class RemoteSync:
    @staticmethod
    def get_creds():
        host = os.environ.get("SFTP_HOST")
        user = os.environ.get("SFTP_USER")
        pas = os.environ.get("SFTP_PASS")
        path = os.environ.get("SFTP_PATH")
        port = int(os.environ.get("SFTP_PORT", 22))

        if not all([host, user, pas, path]):
            log.error("Missing SFTP credentials in .env")
            return None

        return {"remote": {"host": host, "user": user, "pass": pas, "path": path, "port": port}}

    @staticmethod
    def sync_files(files_to_sync, base_dir=ROOT):
        creds = RemoteSync.get_creds()
        if not creds: return False
        remote = creds["remote"]

        transport = None
        try:
            log.info(f"Connecting to {remote['host']}:{remote['port']} (SFTP)...")
            transport = paramiko.Transport((remote["host"], remote["port"]))
            transport.connect(username=remote["user"], password=remote["pass"])
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Navigate to root target
            target_parts = remote["path"].strip("/").split("/")
            for part in target_parts:
                try:
                    sftp.chdir(part)
                except FileNotFoundError:
                    sftp.mkdir(part)
                    sftp.chdir(part)

            for local_rel, remote_rel in files_to_sync.items():
                local_path = base_dir / local_rel
                if not local_path.exists():
                    log.warning(f"Skipping missing file: {local_path}")
                    continue

                # Ensure remote directory exists
                remote_parent = os.path.dirname(remote_rel)
                if remote_parent:
                    parts = remote_parent.split("/")
                    curr_rem = ""
                    for part in parts:
                        if not part: continue
                        curr_rem = f"{curr_rem}/{part}" if curr_rem else part
                        try:
                            sftp.stat(curr_rem)
                        except FileNotFoundError:
                            sftp.mkdir(curr_rem)

                log.info(f"Uploading {local_rel} -> {remote_rel}...")
                sftp.put(str(local_path), remote_rel)
                sftp.chmod(remote_rel, 0o644)

            sftp.close()
            transport.close()
            log.info("Secure SFTP sync completed successfully.")
            return True
        except Exception as e:
            log.error(f"Secure Sync Failed: {e}")
            if transport: transport.close()
            return False

    @staticmethod
    def deploy():
        """Standard deployment for the GPU Tracker."""
        files = {
            "web/index.html": "index.html",
            "database/gpu_intel.js": "database/gpu_intel.js",
            "database/gpu_history.js": "database/gpu_history.js"
        }

        return RemoteSync.sync_files(files)

if __name__ == "__main__":
    RemoteSync.deploy()
