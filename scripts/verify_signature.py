"""
Verify a detached signature for a file using a provided public key PEM.
Usage:
  python scripts/verify_signature.py --file path/to/file --sig path/to/file.sig --pub signing/public_key.pem
Returns exit code 0 on success, 1 on failure.
"""
import argparse
import sys
from pathlib import Path

from infrastructure.crypto import CryptoEngine


def verify(file_path: str, sig_path: str, pub_path: str) -> int:
    try:
        p = Path(file_path)
        s = Path(sig_path)
        pub = Path(pub_path)
        if not p.exists() or not s.exists() or not pub.exists():
            print('Missing file/sig/pub')
            return 2
        data = p.read_bytes()
        signature = s.read_bytes()
        public_pem = pub.read_bytes()

        # Try Ed25519 first
        try:
            ok = CryptoEngine.verify_ed25519(data, signature, public_pem)
            if ok:
                print('Signature verified (ed25519)')
                return 0
        except Exception:
            pass

        # Try RSA-PSS
        try:
            ok = CryptoEngine.verify_rsa_pss(data, signature, public_pem)
            if ok:
                print('Signature verified (rsa-pss)')
                return 0
        except Exception:
            pass

        print('Signature verification failed')
        return 1
    except Exception as e:
        print(f'Unexpected error: {e}')
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify a detached signature')
    parser.add_argument('--file', required=True, help='File to verify')
    parser.add_argument('--sig', required=True, help='Signature file (.sig)')
    parser.add_argument('--pub', required=True, help='Public key PEM')
    args = parser.parse_args()
    sys.exit(verify(args.file, args.sig, args.pub))
