import os
import sys
import tarfile
import urllib
from typing import List

from datasets import Dataset
from loguru import logger

"""

Corpus : Polarity Dataset. Pang/Lee ACL 2004

http://www.cs.cornell.edu/people/pabo/movie-review-data/

"""

corpus_url = (
    "http://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz"
)
corpus_root = os.path.join(os.getcwd(), "review_polarity", "txt_sentoken")
catgeories = ["pos", "neg"]


def download_and_unzip() -> None:
    """
    Download corpus as a zip and then unzip.

    downloads and unzips in the same directory
    by default set to current dir
    """

    file_name = corpus_url.split("/")[-1]
    download_path = os.path.join(os.getcwd(), file_name)
    # where the zip will get extracted
    extracted_path = os.path.join(os.getcwd(), "review_polarity")

    if os.path.exists(extracted_path):
        logger.info("Already downloaded and extracted!")
    else:
        logger.info("Downloading, sit tight!")

        def _progress(count, block_size, total_size):
            sys.stdout.write(
                f"\r>> Downloading {file_name} {float(count * block_size) / float(total_size) * 100.0}%"
            )
            sys.stdout.flush()

        file_path, _ = urllib.request.urlretrieve(corpus_url, download_path, _progress) # type: ignore
        logger.info(
            f"Successfully downloaded {file_name} {os.stat(file_path).st_size} bytes"
        )

        logger.info("Unzipping ...")
        # create dir at extracted_path
        os.mkdir(extracted_path)
        tarfile.open(file_path, "r:gz").extractall(extracted_path)

        # =========================================== clean up
        # delete the downloaded zip file
        logger.info("Deleting downloaded zip file")
        os.remove(file_path)


def read_text_files(path: str) -> List[str]:
    file_list = os.listdir(path)
    texts: List[str] = []

    for fname in file_list:
        fpath = os.path.join(path, fname)

        f = open(fpath, mode="r")
        lines = f.read()
        texts.append(lines)
        f.close()

    return texts


def prepare_dataset() -> Dataset:
    """Collect the raw text files and create a huggingface dataset from them."""

    logger.info("Preparing dataset")
    download_and_unzip()

    dataset_dict = {"text": [], "label": []}

    label_mappings = {"pos": 1, "neg": 0}

    for label_text in ["pos", "neg"]:
        logger.info(f"Processing {label_text} reviews")
        path = os.path.join(corpus_root, label_text)
        texts = read_text_files(path)

        dataset_dict["text"].extend(texts)
        dataset_dict["label"].extend([label_mappings[label_text]] * len(texts))

    logger.info("Creating Dataset from the collected texts and labels")
    dataset = Dataset.from_dict(dataset_dict)
    return dataset
