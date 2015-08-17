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

        self.empty_dir_without_locks = tempfile.mkdtemp()

    def tearDown(self):
        for proc in self.subprocs:
            logging.debug('Killing %s', proc.pid)
            proc.terminate()
        os.rmdir(self.empty_dir_without_locks)
        for tmpf in self.tmpfiles:
            os.unlink(tmpf)
        for tmpd in self.tmpdirs:
            os.removedirs(tmpd)

    def testNoLocks(self):
        self.assertListEqual(
            list(lslocks.lslocks(self.empty_dir_without_locks)),
            [])

    def testDirLock(self):
        dirtolock = tempfile.mkdtemp()
        lockproc = self._lockhelper(dirtolock)
        time.sleep(1)  # Ugly, sorry. Give flock a moment to start up.

        locks = [(pid, path.rstrip('/'))
                 for pid, path in lslocks.lslocks(dirtolock)]
        self.assertEqual(
            locks,
            [(lockproc.pid, dirtolock)])

    def testFileLocks(self):
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
