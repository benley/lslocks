# lslocks

### Install

```sh
python setup.py install
# Or just do:
pip install -r requirements.txt
```

### Usage

```sh
./lslocks.py /directory/name
```

### Running tests

```sh
./lslocks_test.py
```

### Notes

- Symlinks are not followed.
- Only tested on Linux.  Assumes that /proc/locks exists, and that the `flock`
  utility from util-linux is present.
- It was unclear if the file list should be filtered to match \*.lock or not.
  This implementation does not filter like that.
