# Stopped by user — E72 owned jobs

All listed owned process IDs were absent after root's escalated tree termination. The original manifests retain stale `RUNNING`; the operational state is `STOPPED_BY_USER`. No automatic restart is authorized.

Saved small-five completion: 24/52 shards; last independent audit: 21 shards. Saved m03 supplement: 1/11 singleton files. Finished-but-unaudited files are listed explicitly in the JSON checkpoint and have no new central credit.

Byte-exact manifest snapshots, completed-file SHA256 values, pending tasks, known stopped PIDs, and saved resume commands are in `scratch_root_e72_stopped_20260905_1131_checkpoint.json`. Existing proof artifacts and search outputs were not changed.

After an explicit user resume request, audit the finished-but-unaudited files, then run the saved checkpoint runners. They validate and reuse completed files. Do not restart the weaker old m03 full80 job; its stronger full every-depth result is already complete.
