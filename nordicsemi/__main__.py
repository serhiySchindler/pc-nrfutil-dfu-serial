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

import os
import sys
import argparse
import logging
print os.getcwd()
sys.path.append(os.getcwd())

from nordicsemi.dfu.dfu import Dfu
from nordicsemi.dfu.dfu_transport_serial import DfuTransportSerial

logger = logging.getLogger(__name__)


def do_serial(package, port, flow_control = None, packet_receipt_notification = None, baud_rate = None, dfuStart = None):
    if flow_control is None:
        flow_control = DfuTransportSerial.DEFAULT_FLOW_CONTROL
    if packet_receipt_notification is None:
        packet_receipt_notification = DfuTransportSerial.DEFAULT_PRN
    if baud_rate is None:
        baud_rate = DfuTransportSerial.DEFAULT_BAUD_RATE

    logger.info('Programming %s via %s serial port ...' % (package, port, ))

    serial_backend = DfuTransportSerial(com_port=str(port), baud_rate=baud_rate,
                                        flow_control=flow_control, prn=packet_receipt_notification, do_ping=True)
    if dfuStart:
        logger.info('Enterring DFU mode ...')
        serial_backend.send_text_message(dfuStart, flow_control = False)
        logger.info('Done')

    dfu = Dfu(zip_file_path = package, dfu_transport = serial_backend)
    dfu.dfu_send_images()

    logger.info('Device programmed.')


def do_main():
    logging.basicConfig(format = '%(asctime)s %(message)s', level = logging.DEBUG)

    # parse the command line parameters
    # f.e. -pkg app_dfu_package.zip -p COM3
    parser = argparse.ArgumentParser(description = 'Perform a Device Firmware Update over serial transport given a DFU package (zip file).')
    parser.add_argument('-pkg', '--package', dest = 'package', nargs = 1, type = str, required = True,
                        help = "File name of the DFU package.")
    parser.add_argument('-p', '--port', dest = 'port', nargs = 1, type = str, required = True,
                        help = "Serial port address to which the device is connected. (e.g. COM1 in windows systems, /dev/ttyACM0 in linux/mac)")
    parser.add_argument('-dfus', '--dfuStart', dest = 'dfuStart', nargs = '?', type = str, required = False,
                        help = "The dfu entering mode string.")
    args = parser.parse_args()

    try:
        do_serial(package = args.package[0], port = args.port[0], dfuStart = args.dfuStart)
    except:
        logger.exception('')

if __name__ == '__main__':
    do_main()
