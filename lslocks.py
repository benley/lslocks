#!/usr/bin/env python
"""Print PIDs and paths of files locked in a directory tree."""
from __future__ import print_function

import collections
import logging as log
import os
import sys


def gen_imap(rootdir):
    """inode-to-filepath map for descendents of rootdir.

    Args:
        rootdir (String): directory path.

    Returns:
        {inode: {filepath, ...}}
    """

    imap = collections.defaultdict(set)

    def _dopath(base, path=''):
        fpath = os.path.join(base, path)
        try:
            imap[os.stat(fpath).st_ino].add(fpath)
        except OSError as err:
            log.warn('Skipping %s (%s)', fpath, err.strerror)

    for (dirpath, dirnames, filenames) in os.walk(rootdir):
        for dirname in dirnames:
            _dopath(dirpath, dirname)
        for filename in filenames:
            _dopath(dirpath, filename)
    # Include the root directory as well:
    _dopath(rootdir)

    return imap


def read_locks(locks_fh):
    """Process /proc/locks into (inode, pid) tuples.

    Args:
      locks_fh: file-like object

    Yields:
      (inode, pid)
    """

    try:
        while True:
            # locknum: type subtype read/write pid maj:min:inode rStart rEnd
            (_, _, _, _, l_pid, l_fileid, _, _) = locks_fh.next().split()
            _, _, l_inode = l_fileid.split(':')
            yield (l_inode, l_pid)
    except StopIteration:
        return


def filter_locks(locks, inode_map):
    """Filter a set of locks to those matching inode_map.

    Args:
      locks: Iterable of (inode, pid) pairs.
      inode_map: Mapping of {inode: [filepath, ...]}

    Yields:
      (pid, [filepath, ...])
    """
    for (inode, pid) in locks:
        _inode = int(inode)
        if _inode in inode_map:
            yield (pid, inode_map[_inode])


def lslocks(rootpath):
    """Get a map of pids to files locked under rootpath."""
    inode_map = gen_imap(rootpath)

    with open('/proc/locks') as locks_fh:
        locks = filter_locks(read_locks(locks_fh), inode_map)

        for (pid, locked_paths) in locks:
            for path in locked_paths:
                yield (int(pid), path)


def main(argv):
    """Main"""
    if len(argv) != 2:
        myname = os.path.basename(sys.argv[0])
        sys.stderr.write('USAGE: %s <directory>\n' % myname)
        sys.exit(1)

    rootpath = argv[1]

    print('PID\tPath')
    for (pid, path) in lslocks(rootpath):
        print('%s\t%s' % (pid, path))


if __name__ == '__main__':
    main(sys.argv)
