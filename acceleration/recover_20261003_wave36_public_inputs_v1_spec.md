# Exact six-input public recovery wrapper V1

Preserve old five-input wrapper unchanged. This new CI engineering wrapper pins
exactly three package manifests c3efa..., f63943...,38f641... and exactly six raw
paths/hashes. Total242396575 raw bytes/32parts7306880 compressed bytes. The new
one-member package is the full243 coupling fixture; none is a graph resolution.

Use the same unchanged raw recovery CLI d55e458b..., child part/whole SHA256 and
safe nonoverwrite checks. Three child invocations share the outer command's
deadline and reserved20seconds; no solver or mathematical checking. Default
destination is the CI checkout. A clean-recovery caller must provide/assert a
fresh build-only destination and inspect all three RESTORED_MISSING receipts.

Supported CI Windows/Linux command: outer300/worker270;242MiB SHA256/gzip reads
supported by prior five-input9.36second stream audit and one-member1.031second
independent fresh restoration. Positive literal population and strict missing/
duplicate/hash/size controls precede all children. After restoration, independently
recheck all six destination hashes/sizes and receipt counts. Record exact source,
argv,versions,manifest/source pins/actions/receipts,controls and limitations.

This establishes byte recovery engineering only. Public availability requires a
separate immutable remote-byte audit; green CI or recovered hashes do not verify
mathematical claims. Temporary clean build duplicates are not Git payloads.
