"""
Audit logging and backup utilities for file changes.
"""
import json
import os
import time
from pathlib import Path
from typing import Optional

from infrastructure.logger import app_logger
from infrastructure.crypto import CryptoEngine


class Audit:
    LOG_DIR = Path(__file__).parent.parent / "logs" / "audit"
    BACKUP_DIR = LOG_DIR / "backups"
    LOG_FILE = LOG_DIR / "audit.jsonl"

    @classmethod
    def _ensure_dirs(cls):
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _now_ts(cls):
        return int(time.time())

    @classmethod
    def _read_project_config_key(cls) -> Optional[bytes]:
        try:
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config.json"
            if config_path.exists():
                data = json.loads(config_path.read_text(encoding="utf-8"))
                key = data.get("encryption_key")
                if key:
                    return key.encode()
        except Exception:
            pass
        return None

    @classmethod
    def backup_file(cls, file_path: str) -> Optional[str]:
        cls._ensure_dirs()
        try:
            p = Path(file_path)
            if not p.exists():
                return None
            timestamp = cls._now_ts()
            target = cls.BACKUP_DIR / f"{timestamp}_{p.name}.bak"
            with p.open("rb") as src, target.open("wb") as dst:
                dst.write(src.read())
            return str(target)
        except Exception as e:
            app_logger.error(f"Audit backup failed for {file_path}: {e}")
            return None

    @classmethod
    def log_change(cls, file_path: str, action: str, user: str = "local", before_hash: Optional[str] = None, after_hash: Optional[str] = None, signature: Optional[bytes] = None, public_key_pem: Optional[bytes] = None) -> bool:
        cls._ensure_dirs()
        entry = {
            "timestamp": cls._now_ts(),
            "file": str(file_path),
            "action": action,
            "user": user,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "signature_path": None,
            "public_key_path": None,
        }

        # try to write signature and public key files if provided
        try:
            if signature:
                sig_path = cls.LOG_DIR / f"{entry['timestamp']}_{Path(file_path).name}.sig"
                with sig_path.open("wb") as f:
                    f.write(signature)
                entry["signature_path"] = str(sig_path)
            if public_key_pem:
                pub_path = cls.LOG_DIR / f"{entry['timestamp']}_{Path(file_path).name}.pub.pem"
                with pub_path.open("wb") as f:
                    f.write(public_key_pem)
                entry["public_key_path"] = str(pub_path)
        except Exception as e:
            app_logger.error(f"Failed to write signature/public key files: {e}")

        try:
            with cls.LOG_FILE.open("a", encoding="utf-8") as lf:
                lf.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            app_logger.error(f"Failed to append audit log: {e}")
            return False

    @classmethod
    def sign_file_if_possible(cls, file_path: str, after_hash: Optional[str] = None) -> (Optional[bytes], Optional[bytes]):
        """
        Attempt to find encrypted private key and meta in signing/ and sign the file.
        signing/ directory layout expected:
          signing/private_key.enc   (encrypted private key blob)
          signing/meta.json         (contains algorithm: 'rsa' or 'ed25519')
          signing/public_key.pem    (public key PEM)
        Returns (signature_bytes, public_key_pem) or (None, None)
        """
        try:
            project_root = Path(__file__).parent.parent
            signing_dir = project_root / "signing"
            priv_enc = signing_dir / "private_key.enc"
            meta = signing_dir / "meta.json"
            pub_pem = signing_dir / "public_key.pem"
            if not priv_enc.exists() or not meta.exists() or not pub_pem.exists():
                return None, None

            meta_data = json.loads(meta.read_text(encoding="utf-8"))
            algorithm = meta_data.get("algorithm", "rsa")

            # decrypt private key using project config key
            sym_key = cls._read_project_config_key()
            if not sym_key:
                app_logger.error("No encryption key found in config.json for decrypting signing key")
                return None, None

            enc_blob = priv_enc.read_bytes()
            try:
                private_pem = CryptoEngine.decrypt_private_key(enc_blob, sym_key)
            except Exception as e:
                app_logger.error(f"Failed to decrypt private key: {e}")
                return None, None

            # read file bytes and sign
            data = Path(file_path).read_bytes()
            if algorithm == "rsa":
                sig = CryptoEngine.sign_with_rsa_pss(data, private_pem)
            elif algorithm == "ed25519":
                sig = CryptoEngine.sign_with_ed25519(data, private_pem)
            else:
                app_logger.error(f"Unknown signing algorithm in meta: {algorithm}")
                return None, None

            public_pem = pub_pem.read_bytes()
            return sig, public_pem
        except Exception as e:
            app_logger.error(f"sign_file_if_possible failed: {e}")
            return None, None
