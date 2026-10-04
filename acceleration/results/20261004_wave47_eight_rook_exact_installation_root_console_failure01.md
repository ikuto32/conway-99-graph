# Preserved final-display failure after completed installation

The installation command copied the exact checked bytes, passed the closing ledger/HEAD/index guards, and saved the actual installation receipt. Its last display expression then used `TaskNewSha` without `$`, producing an undefined-command error (tool chunk `1a5224`). This happened after the completed mutation and receipt.

The exact original command is preserved alongside this note. A separate read-only observation checked the installed ledger against candidate SHA256 `9eec39f07bb726ddbf69c71ac9df59bdf6fe860a31c69d7513b89ddeb05fc2b1` and the unchanged HEAD/index. The installation was not rerun. No mathematical claim, source artifact, availability record or Git index was changed by the console correction.
