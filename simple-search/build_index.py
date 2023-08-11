import glob
import logging
import argparse
import os
import re
from datetime import datetime
from typing import List
import leveldb
from utils import tokenize_by_CJK_char


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        type=str,
        help="""The dir containing the file to be indexed.
        """,
    )
    parser.add_argument(
        "--db",
        type=str,
        default="db",
        help="""The leveldb path.
        """,
    )
    return parser.parse_args()


def main():
    args = get_args()
    db = leveldb.LevelDB(args.db)
    files = glob.iglob(f"{args.dir}/**/*", recursive=True)
    rindex = {}
    batch = leveldb.WriteBatch()
    logging.info(f"Building reverse index.")
    for i, f in enumerate(files):
        if not os.path.isfile(f):
            continue
        batch.Put(f"doc_{i}".encode(), f.encode())
        fname = os.path.splitext(os.path.basename(f))[0]
        toks = tokenize_by_CJK_char(fname)
        for t in toks:
            if t in rindex:
                rindex[t].append(str(i))
            else:
                rindex[t] = [str(i)]
    for k, v in rindex.items():
        batch.Put(k.encode(), ",".join(v).encode())
    logging.info(f"Write back to leveldb.")
    db.Write(batch, sync = True)
    logging.info(f"Done.")


if __name__=='__main__':
    formatter = (
        "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    )
    now = datetime.now()
    data_time = now.strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs("logs", exist_ok=True)
    log_file_name = f"logs/matching_{data_time}"
    logging.basicConfig(
        level=logging.INFO,
        format=formatter,
        handlers=[logging.FileHandler(log_file_name), logging.StreamHandler()],
    )
    main()
