#
# Copyright (c) 2016 Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
#
#   3. Neither the name of Nordic Semiconductor ASA nor the names of other
#   contributors to this software may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   4. This software must only be used in or with a processor manufactured by Nordic
#   Semiconductor ASA, or in or with a processor manufactured by a third party that
#   is used in combination with a processor manufactured by Nordic Semiconductor.
#
#   5. Any software provided in binary or object form under this license must not be
#   reverse engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import signal

"""nrfutil command line tool."""
import os
import sys
import argparse
import time
import logging
import re
from serial import Serial
sys.path.append(os.getcwd())

from nordicsemi.dfu.dfu import Dfu
from nordicsemi.dfu.dfu_transport import DfuEvent, TRANSPORT_LOGGING_LEVEL
from nordicsemi.dfu.dfu_transport_serial import DfuTransportSerial
from nordicsemi import version as nrfutil_version

logger = logging.getLogger(__name__)


def version():
    """Display nrfutil version."""
    logger.info("nrfutil version {}".format(nrfutil_version.NRFUTIL_VERSION))
    logger.info("PyPi URL: https://pypi.python.org/pypi/nrfutil")
    logger.debug("GitHub URL: https://github.com/NordicSemiconductor/pc-nrfutil")

global_bar = None
def update_progress(progress=0):
    if global_bar:
        global_bar.update(progress)
     
     
def send_text_message(device, baudrate, text, flow_control):
    if not text: # nothing to send
        return

    logger.debug("Serial: send_text_message [%s]" % text)
    try:
        serial = Serial(port=device, baudrate=baudrate, rtscts=flow_control, timeout=2)
        serial.write(text.encode('utf-8'))
        serial.close()
        time.sleep(1)
    except Exception as e:
        logger.exception('send_text_message')
        raise Exception("Serial port could not be opened on {0}. Reason: {1}".format(device, e))




def do_serial(package, port, connect_delay, flow_control, packet_receipt_notification, baud_rate, ping,
              timeout, dfuStart = None):

    if flow_control is None:
        flow_control = DfuTransportSerial.DEFAULT_FLOW_CONTROL
    if packet_receipt_notification is None:
        packet_receipt_notification = DfuTransportSerial.DEFAULT_PRN
    if baud_rate is None:
        baud_rate = DfuTransportSerial.DEFAULT_BAUD_RATE
    if ping is None:
        ping = False
    if port is None:
        raise Exception("Please specify port!")

    if timeout is None:
        timeout = DfuTransportSerial.DEFAULT_TIMEOUT
        
    logger.info("Using board at serial port: {0}, flow_control: {1}, baud_rate: {2}, ping: {3}"
                            .format(port, flow_control, baud_rate, ping))
    serial_backend = DfuTransportSerial(com_port=str(port), baud_rate=baud_rate,
                                        flow_control=flow_control, prn=packet_receipt_notification, do_ping=ping,
                                        timeout=timeout)
    serial_backend.register_events_callback(DfuEvent.PROGRESS_EVENT, update_progress)
    
    if dfuStart:
        logger.info('Enterring DFU mode ...')
        send_text_message(str(port), baud_rate, dfuStart, 1)
        logger.info('Done')
    
    dfu = Dfu(zip_file_path = package, dfu_transport = serial_backend, connect_delay = connect_delay)

    if logger.getEffectiveLevel() > logging.INFO:
        with click.progressbar(length=dfu.dfu_get_total_size()) as bar:
            global global_bar
            global_bar = bar
            dfu.dfu_send_images()
    else:
        dfu.dfu_send_images()

    logger.info("Device programmed.")



def do_main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    #root = logging.getLogger('')
    #fh = logging.FileHandler('test.txt')
    #fh.setLevel(logging.DEBUG)
    #fh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    #root.addHandler(fh)
    
    # parse the command line parameters
    # f.e. -pkg app_dfu_package.zip -p COM3
    parser = argparse.ArgumentParser(description = 'Perform a Device Firmware Update over serial transport given a DFU package (zip file).')
    parser.add_argument('-pkg', '--package', dest = 'package', nargs = 1, type = str, required = True,
                        help = "File name of the DFU package.")
    parser.add_argument('-p', '--port', dest = 'port', nargs = 1, type = str, required = True,
                        help = "Serial port address to which the device is connected. (e.g. COM1 in windows systems, /dev/ttyACM0 in linux/mac)")
    parser.add_argument('-dfus', '--dfuStart', dest = 'dfuStart', nargs = '?', type = str, required = False,
                        help = "The dfu entering mode string.")
    parser.add_argument('-fc', '--flow-control', dest = 'fc', nargs = 1, type = int, required = False,
                        help = "To enable flow control set this flag to 1.")
    parser.add_argument('-t', '--timeout', dest = 'fc', nargs = 1, type = int, required = False,
                        help = "Set the timeout in seconds for board to respond (default: 30 seconds).")
    parser.add_argument("-v", "--version", action="store_true",
                        help = "get Version info")
    args = parser.parse_args()
    
    if args.version:
        version()
    
    try:
        do_serial(package = args.package[0], port = args.port[0], connect_delay = 0, 
                flow_control = args.fc[0], packet_receipt_notification = None , 
                baud_rate = 115200, ping = False, timeout = 2, dfuStart = args.dfuStart)
    except:
        logger.exception('')


if __name__ == '__main__':
    do_main()
