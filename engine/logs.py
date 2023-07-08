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
import logging
import os
import threading

from reportportal_client.helpers import timestamp
from daksha.settings import LOG_FILE,REPORT_PORTAL_ENABLED,report_portal_service

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Logging configs
logFormatter = logging.Formatter('%(asctime)s [%(levelname)-7.7s]  %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileHandler = logging.FileHandler(LOG_FILE)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

if(REPORT_PORTAL_ENABLED != None and REPORT_PORTAL_ENABLED.lower() == "true"):
    class ReportPortalLoggingHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.thread_local = threading.local()
            #threading.local() is used to create a unique thread-local object
        
        def set_item_id(self, item_id):
            self.thread_local.item_id = item_id

        def clear_item_id(self):
            if hasattr(self.thread_local, 'item_id'):
                del self.thread_local.item_id

        def emit(self, record):
            # Get the log message and level
            msg = self.format(record)
            level = record.levelname

            screenshot = record.__dict__.get('screenshot')
            attachment={"data": screenshot, "mime": "image/png"}
            # Get the current thread's item ID from thread-local storage
            item_id = getattr(self.thread_local, 'item_id', None)

            # Send the log message to Report Portal using the current item ID
            if(item_id != None):
                if(screenshot != None):
                    report_portal_service.log(time=timestamp(), attachment=attachment, message=msg, level=level, item_id=item_id)
                else:
                    report_portal_service.log(time=timestamp(),message=msg, level=level, item_id=item_id)

    report_portal_logging_handler = ReportPortalLoggingHandler()
    logger.addHandler(report_portal_logging_handler)

