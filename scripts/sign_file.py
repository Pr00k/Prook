"""
Sign a file using the encrypted private key in signing/private_key.enc.
Writes a detached signature next to the file (filename.sig) and logs the change via Audit.
Usage:
  python scripts/sign_file.py --file path/to/file --passphrase "your passphrase"
If --passphrase is omitted the script will prompt interactively.
"""
import argparse
import getpass
from pathlib import Path
import json
import sys

from infrastructure.crypto import CryptoEngine
from infrastructure.audit import Audit


def sign_file(file_path: str, passphrase: bytes) -> int:
    try:
        p = Path(file_path)
        if not p.exists():
            print(f"File not found: {file_path}")
            return 2

        project_root = Path(__file__).parent.parent
        signing_dir = project_root / 'signing'
        priv_enc = signing_dir / 'private_key.enc'
        meta = signing_dir / 'meta.json'
        pub_pem = signing_dir / 'public_key.pem'

        if not priv_enc.exists() or not meta.exists() or not pub_pem.exists():
            print('Signing keys not found in signing/ - generate or import keys first')
            return 3

        meta_data = json.loads(meta.read_text(encoding='utf-8'))
        algorithm = meta_data.get('algorithm', 'rsa')

        enc_blob = priv_enc.read_bytes()
        # decrypt private key using given passphrase bytes
        try:
            private_pem = CryptoEngine.decrypt_private_key(enc_blob, passphrase)
        except Exception as e:
            print(f"Failed to decrypt private key: {e}")
            return 4

        data = p.read_bytes()
        if algorithm == 'ed25519':
            sig = CryptoEngine.sign_with_ed25519(data, private_pem)
        else:
            sig = CryptoEngine.sign_with_rsa_pss(data, private_pem)

        sig_path = p.with_suffix(p.suffix + '.sig') if p.suffix else Path(str(p) + '.sig')
        sig_path.write_bytes(sig)

        # attach public key bytes for audit log
        public_pem_bytes = pub_pem.read_bytes()

        # compute before/after hashes (before hash may be None here)
        after_hash = CryptoEngine.sha256(data)

        Audit.log_change(str(p), action='sign', user='local', before_hash=None, after_hash=after_hash, signature=sig, public_key_pem=public_pem_bytes)

        print(f"Signed {file_path} -> {sig_path}")
        return 0
    except Exception as e:
        print(f"Unexpected error signing file: {e}")
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sign a file using the project signing key')
    parser.add_argument('--file', required=True, help='File to sign')
    parser.add_argument('--passphrase', required=False, help='Passphrase to decrypt private key (omit to be prompted)')
    args = parser.parse_args()

    if args.passphrase:
        passphrase = args.passphrase.encode()
    else:
        p = getpass.getpass('Enter passphrase to decrypt private key: ')
        passphrase = p.encode()

    sys.exit(sign_file(args.file, passphrase))
