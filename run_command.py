#!/usr/bin/env python3

# Run a command on the hub.
# Guts were lifted from spikeprime-tools/spiketools/spikejsonrpcapispike.py

import base64
from comm.DirectConnectionMonitor import DirectConnectionMonitor
from comm.UsbConnectionMonitor import UsbConnectionMonitor
from comm.SerialConnection import SerialConnection
import os
import argparse
from tqdm import tqdm
import time
import json
import logging
from datetime import datetime
from comm.HubClient import ConnectionState, HubClient
from utils.setup import setup_logging

logger = logging.getLogger("App")


class RPC:
  def __init__(self):
    cm = UsbConnectionMonitor()
    # below is an alternative if the USB scanning does not work
    #cm = DirectConnectionMonitor(SerialConnection("/dev/ttyACM0"))
    self._client = HubClient(cm)
    self._client.start()

  def send_message(self, name, params = {}):
    while rpc._client.state is not ConnectionState.TELEMETRY:
      logger.info('waiting for hub to connect')
      time.sleep(2)
    return self._client.send_message(name, params)

# Program Methods
  def program_execute(self, n):
    return self.send_message('program_execute', {'slotid': n})

  def program_terminate(self):
    return self.send_message('program_terminate')

  def get_storage_information(self):
    return self.send_message('get_storage_status')

  def start_write_program(self, name, size, slot, created, modified):
    meta = {'created': created, 'modified': modified, 'name': name, 'type': 'python', 'project_id': '50uN1ZaRpHj2'}
    return self.send_message('start_write_program', {'slotid':slot, 'size': size, 'meta': meta})

  def write_package(self, data, transferid):
    return self.send_message('write_package', {'data': str(base64.b64encode(data), 'utf-8'), 'transferid': transferid})

  def move_project(self, from_slot, to_slot):
    return self.send_message('move_project', {'old_slotid': from_slot, 'new_slotid': to_slot})

  def remove_project(self, from_slot):
    return self.send_message('remove_project', {'slotid': from_slot })

# Light Methods
  def display_set_pixel(self, x, y, brightness = 9):
    return self.send_message('scratch.display_set_pixel', { 'x':x, 'y': y, 'brightness': brightness})

  def display_clear(self):
    return self.send_message('scratch.display_clear')

  def display_image(self, image):
    return self.send_message('scratch.display_image', { 'image':image })

  def display_image_for(self, image, duration_ms):
    return self.send_message('scratch.display_image_for', { 'image':image, 'duration': duration_ms })

  def display_text(self, text):
    return self.send_message('scratch.display_text', {'text':text})

# Hub Methods
  def get_firmware_info(self):
    return self.send_message('get_hub_info')


if __name__ == "__main__":
  def handle_list():
    info = rpc.get_storage_information()
    storage = info['storage']
    slots = info['slots']
    print("%4s %-40s %6s %-20s %-12s %-10s" % ("Slot", "Decoded Name", "Size",  "Last Modified", "Project_id", "Type"))
    for i in range(20):
      if str(i) in slots:
        sl = slots[str(i)]
        modified = datetime.utcfromtimestamp(sl['modified']/1000).strftime('%Y-%m-%d %H:%M:%S')
        try:
          decoded_name = base64.b64decode(sl['name']).decode('utf-8')
        except:
          decoded_name = sl['name']
        try:
          project = sl['project_id']
        except:
          project = " "
        try:
          type = sl['type']
        except:
          type = " "
        # print("%2s %-40s %-40s %5db %6s %-20s %-20s %-10s" % (i, sl['name'], decoded_name, sl['size'], sl['id'], modified, project, type))
        print("%4s %-40s %5db %-20s %-12s %-10s" % (i, decoded_name, sl['size'], modified, project, type))
    print(("Storage free %s%s of total %s%s" % (storage['free'], storage['unit'], storage['total'], storage['unit'])))
  
  def handle_fwinfo():
    info = rpc.get_firmware_info()
    fw = '.'.join(str(x) for x in info['firmware']['version'])
    rt = '.'.join(str(x) for x in info['runtime']['version'])
    print("Firmware version: %s; Runtime version: %s" % (fw, rt))
  
  def handle_upload():
    with open(args.file, "rb") as f:
      size = os.path.getsize(args.file)
      name = args.name if args.name else args.file
      now = int(time.time() * 1000)
      start = rpc.start_write_program(name, size, args.to_slot, now, now)
      bs = start['blocksize']
      id = start['transferid']
      with tqdm(total=size, unit='B', unit_scale=True) as pbar:
        b = f.read(bs)
        while b:
          rpc.write_package(b, id)
          pbar.update(len(b))
          b = f.read(bs)
      if args.start:
        rpc.program_execute(args.to_slot)

  parser = argparse.ArgumentParser(description='Tools for Spike Hub RPC protocol')
  parser.add_argument('--verbose', help='print informational messages to console', action='store_true')
  parser.set_defaults(func=lambda: parser.print_help())
  sub_parsers = parser.add_subparsers()

  list_parser = sub_parsers.add_parser('list', aliases=['ls'], help='List stored programs')
  list_parser.set_defaults(func=handle_list)

  fwinfo_parser = sub_parsers.add_parser('fwinfo', help='Show firmware version')
  fwinfo_parser.set_defaults(func=handle_fwinfo)

  mvprogram_parser = sub_parsers.add_parser('mv', help='Changes program slot')
  mvprogram_parser.add_argument('from_slot', type=int)
  mvprogram_parser.add_argument('to_slot', type=int)
  mvprogram_parser.set_defaults(func=lambda: rpc.move_project(args.from_slot, args.to_slot))

  cpprogram_parser = sub_parsers.add_parser('upload', aliases=['cp'], help='Uploads a program')
  cpprogram_parser.add_argument('file')
  cpprogram_parser.add_argument('to_slot', type=int)
  cpprogram_parser.add_argument('name', nargs='?')
  cpprogram_parser.add_argument('--start', '-s', help='Start after upload', action='store_true')
  cpprogram_parser.set_defaults(func=handle_upload)

  rmprogram_parser = sub_parsers.add_parser('rm', help='Removes the program at a given slot')
  rmprogram_parser.add_argument('from_slot', type=int)
  rmprogram_parser.set_defaults(func=lambda: rpc.remove_project(args.from_slot))

  startprogram_parser = sub_parsers.add_parser('start', help='Starts a program')
  startprogram_parser.add_argument('slot', type=int)
  startprogram_parser.set_defaults(func=lambda: rpc.program_execute(args.slot))

  stopprogram_parser = sub_parsers.add_parser('stop', help='Stop program execution')
  stopprogram_parser.set_defaults(func=lambda: rpc.program_terminate())

  display_parser = sub_parsers.add_parser('display', help='Controls 5x5 LED matrix display')
  display_parser.set_defaults(func=lambda: display_parser.print_help())
  display_parsers = display_parser.add_subparsers()

  display_image_parser = display_parsers.add_parser('image', help='Displays image on the LED matrix')
  display_image_parser.add_argument('image', help='format xxxxx:xxxxx:xxxxx:xxxxx:xxxx, where x is the pixel brigthness in range 0-9')
  display_image_parser.set_defaults(func=lambda: rpc.display_image(args.image))

  display_text_parser = display_parsers.add_parser('text', help='Displays scrolling text on the LED matrix')
  display_text_parser.add_argument('text')
  display_text_parser.set_defaults(func=lambda: rpc.display_text(args.text))

  display_clear_parser = display_parsers.add_parser('clear', help='Clears display')
  display_clear_parser.set_defaults(func=lambda: rpc.display_clear())

  display_pixel_parser = display_parsers.add_parser('setpixel', help='Sets individual LED brightness')
  display_pixel_parser.add_argument('x', type=int)
  display_pixel_parser.add_argument('y', type=int)
  display_pixel_parser.add_argument('brightness', nargs='?', type=int, default=9, help='pixel brightness 0-9')
  display_pixel_parser.set_defaults(func=lambda: rpc.display_set_pixel(args.x, args.y, args.brightness))

  log_level = logging.WARNING
  args = parser.parse_args()
  if args.verbose:
    log_level = logging.DEBUG

  setup_logging(os.path.dirname(__file__) + "/logs/run_command.log", log_level)

  rpc = RPC()
  args.func()
