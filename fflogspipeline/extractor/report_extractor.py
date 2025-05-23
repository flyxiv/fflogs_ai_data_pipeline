"""Class for extracting logs that are linked from a URL.

run example: in fflogs_ai_data_pipeline directory,

```sh
python -m fflogspipeline.extractor.report_extractor --fflogs-ranking-url ./fflogspipeline/extractor/ninja_ranking_urls.yml
```
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from typing import List
from pathlib import Path

import argparse
import logging
import re
import pathlib
import yaml
import tqdm
import logging

from ..util import HTTP_RESPONSE_OK
from ..rotationlog.fflogs_report_parser import FflogsReportParser

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fflogs-ranking-url", type=str, required=False, help="path to the file that contains the URL of the job's ranking page")
    return parser.parse_args()

class ReportExtractor:
    """Extracts URL of logs inside a DPS ranking directory.

    We only need quality logs, so we gather logs ranked highest
    in the job DPS rankings. To do that,

    1) We pass the URL of the job's ranking page
    2) Extractor gets the content of the page, and scrapes all text that starts with '/reports/'
    """

    # Amount of seconds to wait to give time so that the dynamic content of the page generates.
    WAIT_SECONDS = 3

    # if the url is /reports/AB2331DEES?time=64, only parse the report key = AB2331DEES
    REPORT_PARSE_REGEX_STRING = r"/reports/([^?]+)\?"

    def __init__(self, config_file_path: str):
        try:
            with open(config_file_path, "r") as config_yaml_file:
                config = yaml.load(config_yaml_file, yaml.FullLoader)
                ranking_urls = config["urls"]

                self._find_all_reports_to_parse(ranking_urls)
                self.reports_to_parse = sum(self.reports_to_parse, list())

                logging.info(
                    f"number of reports to parse: {len(self.reports_to_parse)}"
                )

        except IOError:
            error_msg = f"cannot find file {config_file_path}"
            logging.error(error_msg)

            raise IOError(error_msg)

    def _find_all_reports_to_parse(self, ranking_urls: List[str]):
        """Find all urls in the ranking page that start with '/reports/'

        Return a blank list and print an error if ranking_url request gives error
        """
        self.reports_to_parse = list()

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)

        for ranking_url in ranking_urls:
            logging.info(f"collecting {ranking_url}..")
            driver.get(ranking_url)

            driver.implicitly_wait(self.WAIT_SECONDS)
            self.reports_to_parse.append(
                self._parse_reports_to_read(driver.page_source)
            )

        driver.quit()

    def _parse_reports_to_read(self, ranking_url_body_text: str):
        """Get all reports in the ranking URL that are not in data directory

        If the report ID is in the data url, then the report is already collected,
        so skip the report.
        """
        report_keys = re.findall(self.REPORT_PARSE_REGEX_STRING, ranking_url_body_text)
        logging.info(f"report keys found: f{report_keys}")

        data_dir = pathlib.Path.cwd() / "data"
        report_keys_already_collected = {
            json_file.stem for json_file in data_dir.rglob("*.json")
        }

        report_keys_not_collected_yet = set(report_keys) - report_keys_already_collected
        return list(report_keys_not_collected_yet)

    def parse_reports(self):
        report_parser = FflogsReportParser()
        for report_key in tqdm.tqdm(self.reports_to_parse):
            report_parser.parse_report(report_key)


if __name__ == "__main__":
    args = parse_args()

    if args.fflogs_ranking_url:
        report_extractor = ReportExtractor(args.fflogs_ranking_url)
    else:
        _EXTRACTOR_FILE_DIR = Path(__file__).resolve().parent

        report_extractor = ReportExtractor(
            _EXTRACTOR_FILE_DIR / "./ninja_ranking_urls.yml"
        )

    report_extractor.parse_reports()

    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
