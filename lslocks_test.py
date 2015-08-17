#!/usr/bin/env python
"""Tests for lslocks."""

import logging
import os
import tempfile
import time
import unittest
import subprocess

import lslocks


class LslocksTests(unittest.TestCase):
    """Tests for lslocks.

    Using flock(1) from util-linux instead of python's fcntl module because the
    instructions asked for subprocesses.

    Probably could have used fork() or multiprocessing to stay python native
    and not assume anything about what system we're running on, if necessary.
    """

    def _lockhelper(self, path):
        proc = subprocess.Popen(
            ['flock', path, '-c', 'while true; do sleep 10; done'])
        self.subprocs.append(proc)
        logging.debug('Locking %s', path)
        return proc

    def setUp(self):
        self.subprocs = []
        self.tmpdirs = []
        self.tmpfiles = []

    def tearDown(self):
        for proc in self.subprocs:
            logging.debug('Killing %s', proc.pid)
            proc.terminate()
        for tmpf in self.tmpfiles:
            os.unlink(tmpf)
        for tmpd in self.tmpdirs:
            os.removedirs(tmpd)

    def testNoLocks(self):
        """Verify that it doesn't find anything when there are no locks."""
        emptydir = tempfile.mkdtemp()
        self.tmpdirs.append(emptydir)
        self.assertListEqual(
            list(lslocks.lslocks(emptydir)),
            [])

    def testDirLock(self):
        """Lock a directory, check that lslocks sees it."""
        dirtolock = tempfile.mkdtemp()
        lockproc = self._lockhelper(dirtolock)
        time.sleep(1)  # Ugly, sorry. Give flock a moment to start up.

        locks = [(pid, path.rstrip('/'))
                 for pid, path in lslocks.lslocks(dirtolock)]
        self.assertEqual(
            locks,
            [(lockproc.pid, dirtolock)])

    def testFileLocks(self):
        """Lock several files, verify that lslocks finds all of them."""
        basedir = tempfile.mkdtemp()
        self.tmpdirs.append(basedir)
        locked_files = [tempfile.mkstemp(dir=basedir)[1]
                        for _ in range(10)]
        self.tmpfiles.extend(locked_files)
        expected_locks = set()

        for tmpf in locked_files:
            proc = self._lockhelper(tmpf)
            expected_locks.add((proc.pid, tmpf.rstrip('/')))

        time.sleep(1)  # Ugly, sorry. Give flock a moment to start up.

        locks = {(pid, path.rstrip('/'))
                 for pid, path in lslocks.lslocks(basedir)}
        self.assertSetEqual(expected_locks, locks)


if __name__ == '__main__':
    unittest.main()
