# `split-patch.py`

[![asciicast](demo.gif)](https://asciinema.org/a/H69kggNt02RmU8sQxX2P5vlJI)

This is `git add -p` on steroids for patches.

Given a `my.patch` you can run

    ./split-patch.py my.patch

You can choose in which *bucket* to put each hunk.

At any moment, you can quit and `my.patch` will contain unassigned hunks while all the other hunks will be moved to `$BUCKET_NAME.patch`.

## `git-split-commit`

The `git-split-commit` command uses `split-patch.py` to split the `HEAD` commit in multiple commits.

    # Create backup tag
    git tag backup-$(date +'%s')

    # Split HEAD
    ./git-split-commit

By default, it first `git revert HEAD` and then commit all the patches resulting from the split.

If you don't care about the original commit + revert commit pair, you can run:

    ./git-split-commit --reset

## Usage in interactive rebase

You can use `git-split-commit` during interactive rebase, assuming you have it in `$PATH`:

    git rebase -i HEAD^^^^

Your `$EDITOR` will pop up with a series of `pick` commands.
After the commit you want to split add:

    exec git split-commit
