"""Recover byte-identical, hash-bound research inputs from published gzip files."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    rows = json.loads(args.manifest.read_bytes())['files']
    for row in rows:
        target = (root / row['path']).resolve()
        source = (root / row['compressed_path']).resolve()
        if not target.is_relative_to(root) or not source.is_relative_to(root):
            raise ValueError('Artifact path outside repository')
        compressed = source.read_bytes()
        if sha256(compressed).hexdigest() != row['compressed_sha256']:
            raise ValueError(f'Compressed hash mismatch: {source}')
        data = gzip.decompress(compressed)
        if len(data) != row['size_bytes'] or sha256(data).hexdigest() != row['sha256']:
            raise ValueError(f'Recovered bytes mismatch: {target}')
        if target.exists():
            if target.read_bytes() != data:
                raise ValueError(f'Refusing to overwrite different artifact: {target}')
            state = 'already identical'
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
            state = 'restored'
        print(f'{row["path"]}: {state}; SHA256 {row["sha256"]}')


if __name__ == '__main__':
    main()
