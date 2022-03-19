# `split-patch.py`

[![asciicast](demo.gif)](https://asciinema.org/a/H69kggNt02RmU8sQxX2P5vlJI)

This is `git add -p` on steroids for patches.

Given a `my.patch` you can run

    ./split-patch.py my.patch

You can choose in which *bucket* to put each hunk.

In any moment, you can quit and `my.patch` will contain unassigned hunks while all the other hunks will be moved to `$BUCKET_NAME.patch`.

