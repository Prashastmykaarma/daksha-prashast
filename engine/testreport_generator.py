"""
Daksha
Copyright (C) 2021 myKaarma.
opensource@mykaarma.com
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import json
import os
import shutil
import string
import random

from .logs import logger

from daksha.settings import STORAGE_PATH
from .models import TestResult
from datetime import datetime


def generate_result(test_id, response, name, step, error_stack):
    """
    Generates Test Result
     :param test_id: ID of the Test
     :type test_id: str
     :param response: Execution Status
     :type response: bool
     :param step : Last executed step of the Test
     :type step: dict
     :param error_stack: Error Stack if Test failed
     :type error_stack: str
     :param name: Name of the Test mentioned in YAML
     :type name: str
    """
    try:
        logger.info('Creating test result')
        time_now = datetime.now()
        processed_time_now = time_now.__str__().replace(":", "_")
        result_file_path = f"{STORAGE_PATH}/{test_id}/result/{name}_{processed_time_now}"
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        if response:
            test_status = "Passed"
            step = ""
            error_stack = ""

        else:
            test_status = "Failed"
            error_stack = error_stack.replace('<', '&lt;').replace('>', '&gt;')
        test_result = TestResult(name, test_status, step.__str__(), error_stack)
        
        with open(result_file_path, 'w') as f:
            json.dump(test_result.__dict__, f)
        f.close()
    except Exception:
        logger.error("Error in test result generation:", exc_info=True)


def generate_test_id():
    """
    Generates an unique 11 Digit Test ID
     :returns : 11 Digit unique Test ID
     :rtype: str
    """
    res = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=11))
    logger.info("Test ID: " + res)
    return res


def generate_report(test_id):
    """
    Generates Test Report
     :param test_id: ID of the Test
     :type test_id: str
    """
    try:
        logger.info('Creating test report')
        passed_count, failed_count = 0, 0
        test_result = []
        result_folder_path = f"{STORAGE_PATH}/{test_id}/result"
        for file in os.listdir(result_folder_path):
            result_file_path = os.path.join(result_folder_path, file)
            with open(result_file_path) as f:
                for line in f:
                    test_result.append(json.loads(line.strip()))
                    if json.loads(line)["test_status"] == "Passed":
                        passed_count += 1
                    else:
                        failed_count += 1
        test_result = json.dumps(test_result)
        replacement = {"test_id": test_id, "test_result": test_result, "passed_count": passed_count.__str__(),
                       "failed_count": failed_count.__str__()}

        report_file_dir = f"{STORAGE_PATH}/{test_id}/"
        shutil.copy("templates/report.html", report_file_dir)
        shutil.copy("templates/report.js", report_file_dir)
        shutil.copy("templates/report.css", report_file_dir)
        with open(f"{report_file_dir}/report.html", "r+") as file:
            content = string.Template(file.read()).substitute(**replacement)
            file.seek(0)
            file.write(content)
            file.truncate()
        with open(f"{report_file_dir}/report.js", "r+") as file:
            content = string.Template(file.read()).substitute(**replacement)
            file.seek(0)
            file.write(content)
            file.truncate()
        logger.info("Test Report generated")
    except Exception:
        logger.error("Error in test report generation:", exc_info=True)

