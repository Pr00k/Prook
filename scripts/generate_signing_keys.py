"""
Key generation CLI for signing: generates Ed25519 and RSA-PSS keypairs,
encrypts private keys using a passphrase or config key, and writes
signing/private_key.enc, signing/public_key.pem, signing/meta.json.
"""
import os
import json
import argparse
import getpass
from pathlib import Path

from infrastructure.crypto import CryptoEngine


def generate(args):
    project_root = Path(__file__).parent.parent
    signing_dir = project_root / "signing"
    signing_dir.mkdir(parents=True, exist_ok=True)

    algo = args.algorithm.lower()
    use_pass = args.passphrase is None

    if algo == "ed25519":
        pub, priv = CryptoEngine.generate_ed25519_keypair()
    elif algo == "rsa":
        pub, priv = CryptoEngine.generate_rsa_keypair(key_size=args.rsa_bits)
    else:
        print(f"Unknown algorithm: {args.algorithm}")
        return 1

    # determine encryption key
    if args.passphrase:
        passphrase = args.passphrase.encode()
    else:
        # ask interactively
        p1 = getpass.getpass("Enter passphrase to encrypt private key: ")
        p2 = getpass.getpass("Confirm passphrase: ")
        if p1 != p2:
            print("Passphrases do not match")
            return 1
        passphrase = p1.encode()

    # encrypt private key
    enc_blob = CryptoEngine.encrypt_private_key(priv, passphrase)

    priv_path = signing_dir / "private_key.enc"
    pub_path = signing_dir / "public_key.pem"
    meta_path = signing_dir / "meta.json"

    priv_path.write_bytes(enc_blob)
    pub_path.write_bytes(pub)
    meta = {
        "algorithm": algo,
        "rsa_bits": args.rsa_bits if algo == "rsa" else None
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Generated signing keys:")
    print(f"  public key: {pub_path}")
    print(f"  encrypted private key: {priv_path}")
    print(f"  meta: {meta_path}")
    print("Store the private_key.enc and passphrase securely. Do NOT commit them to the repository.")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate signing keypair for ProokSuite')
    parser.add_argument('--algorithm', choices=['ed25519', 'rsa'], default='ed25519', help='Signing algorithm')
    parser.add_argument('--rsa-bits', type=int, default=4096, help='RSA key size (if rsa chosen)')
    parser.add_argument('--passphrase', type=str, default=None, help='Provide passphrase to encrypt private key (omit to be prompted)')
    args = parser.parse_args()
    raise SystemExit(generate(args))
