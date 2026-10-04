# Pre-worker launch correction

Root's first nine-claim typed launch returned a PowerShell ParserError before
any statement executed or supervisor/worker/output/ONE was created. JavaScript
String.replace interpreted a dollar followed by a single quote in the inserted
PowerShell regex as replacement-tail syntax. The correction constructs the
guard as a raw literal and concatenates the original prefix and suffix, with
one worker declaration and one process inventory. No computational attempt,
mathematical result or original research evidence is changed. The corrected
ONE command and actual supervisor outputs provide the executed command record.
