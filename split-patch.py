#!/usr/bin/env python

import argparse
import os
import readline
import sys
import subprocess
import shutil

from tempfile import NamedTemporaryFile

from termcolor import colored

from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import TerminalFormatter

from collections import defaultdict
from unidiff import PatchSet

args = None
patch = None
buckets = defaultdict(list)
all_assigned_hunks = set()


def warning(message):
    print(colored(message, "red"))


def print_buckets():
    for bucket in buckets:
        print(f"  {bucket}")


def create_new_bucket(name):
    if name in buckets:
        return False

    buckets[name] = []

    return True


def assign_to(path, hunk, name):
    if name not in buckets:
        if os.path.isfile(f"{name}.patch"):
            ask(f"{name}.patch exists, appending there. ")
            create_new_bucket(name)
        else:
            return False

    all_assigned_hunks.add(id(hunk))
    buckets[name] += [(path, hunk)]

    return True


def print_hunk(path, hunk, force_less=False):

    text = highlight(diff_header(path) + str(hunk), DiffLexer(), TerminalFormatter())
    global args
    if force_less or not args.no_less and text.count("\n") + 1 > shutil.get_terminal_size().lines:
        with NamedTemporaryFile(suffix=".patch", mode="w") as temp_file:
            temp_file.write(text)
            temp_file.flush()
            subprocess.run(["less", "-R", temp_file.name])

    print(chr(27) + "[2J")
    print(text)


def diff_header(path):
    return f"--- a/{path}\n+++ a/{path}\n"


def save_patches():
    for bucket_name, hunks in buckets.items():
        with open(f"{bucket_name}.patch", "a") as bucket_file:
            old_path = ""
            for (path, hunk) in sorted(hunks, key=lambda a: a[0]):
                if path != old_path:
                    old_path = path
                    bucket_file.write(diff_header(path))
                bucket_file.write(str(hunk))

    with open(args.patch, "w") as patch_file:
        for patched_file in patch:
            path = patched_file.path
            first = True
            for hunk in patched_file:
                if id(hunk) not in all_assigned_hunks:
                    if first:
                        first = False
                        patch_file.write(diff_header(path))
                    patch_file.write(str(hunk))


def is_assigned(index):
    current_index = 0
    for patched_file in patch:
        for hunk in patched_file:
            if index == current_index:
                return id(hunk) in all_assigned_hunks
            current_index += 1
    assert False


def done():
    while True:
        command = ask("We're done. Save? [yn] ")
        if command == "y":
            save_patches()
            sys.exit(0)
        elif command == "n":
            sys.exit(0)


def next(bumping=False):
    global target_index
    global total_hunks
    first = True
    while first or is_assigned(target_index):
        first = False
        if target_index == total_hunks - 1:
            if not bumping:
                ask("You're at the last hunk! ")
                if is_assigned(target_index):
                    previous(True)
            else:
                done()
            return
        else:
            target_index += 1


def previous(bumping=False):
    global target_index
    first = True
    while first or is_assigned(target_index):
        first = False
        if target_index == 0:
            if not bumping:
                ask("You're at the first hunk! ")
                if is_assigned(target_index):
                    next(True)
            else:
                done()
            return
        else:
            target_index -= 1


def ask(message):
    try:
        return input(colored(message, "blue"))
    except (KeyboardInterrupt, EOFError):
        print()
        print("Exiting without saving")
        sys.exit(1)


def handle_hunk(patched_file, hunk):
    hunks_count = len(patched_file)
    index_in_file = [
        index for index, current_hunk in enumerate(patched_file) if id(hunk) == id(current_hunk)
    ][0]
    print_hunk(patched_file.path, hunk)
    retry = False
    global last_command
    global command
    last_command = command
    input_message = f"#({target_index+1}/{total_hunks}) ({index_in_file+1}/{hunks_count}) Target bucket [?,!BUCKET,BUCKET,p,n,q,l]"
    if last_command:
        input_message += f" (last command: {command})"
    input_message += ": "
    command = ask(input_message)

    if len(command) == 0:
        command = last_command

    if command == "?":
        print_buckets()
    elif command.startswith("!"):
        command = command[1:]
        if not create_new_bucket(command):
            ask(f'Cannot create bucket "{command}"! ')
        else:
            assign_to(patched_file.path, hunk, command)
            next()
    elif command == "l":
        print_hunk(patched_file.path, hunk, True)
    elif command == "n":
        next()
    elif command == "p":
        previous()
    elif command == "q":
        save_patches()
        sys.exit(0)
    else:
        if not assign_to(patched_file.path, hunk, command):
            ask(f'Bucket "{command}" does not exists! ')
        else:
            next()


def main():
    parser = argparse.ArgumentParser(description="Organize patch in buckets.")
    parser.add_argument("patch", metavar="PATCH", help="input patch")
    parser.add_argument("--no-less", action="store_true", help="Don't use less.")
    global args
    args = parser.parse_args()

    global patch
    patch = PatchSet(open(args.patch, "r"))

    global command
    command = ""

    files_count = len(patch)
    global target_index
    target_index = 0

    global total_hunks
    total_hunks = 0
    for patched_file in patch:
        for hunk in patched_file:
            total_hunks += 1

    while True:
        global index
        index = 0
        for file_index, patched_file in enumerate(patch):
            path = patched_file.path
            hunks_count = len(patched_file)
            warning(f"({file_index+1}/{files_count}) Patched file: {path} ({hunks_count} hunks)")
            for hunk in patched_file:
                if index == target_index:
                    handle_hunk(patched_file, hunk)
                index += 1


if __name__ == "__main__":
    sys.exit(main())
