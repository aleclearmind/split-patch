# `split-patch.py`

This is `git add -p` on steroids for patches.

Given a `my.patch` you can run

    ./split-patch.py my.patch

You can choose in which *bucket* to put each hunk.

In any moment, you can quite and `my.patch` will contain unassigned hunks while all the other hunks will be moved to `$BUCKET_NAME.patch`.

