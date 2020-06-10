#!/usr/bin/env python3

import tango
import datetime
import argparse
import time


EVENT_TYPES = {"periodic": tango.EventType.PERIODIC_EVENT,
               "change": tango.EventType.CHANGE_EVENT,
               "archive": tango.EventType.ARCHIVE_EVENT,
               "data_ready": tango.EventType.DATA_READY_EVENT}

# PIPE_EVENT
# ATTR_CONF_EVENT
# QUALITY_EVENT
# USER_EVENT
# INTERFACE_CHANGE_EVENT


def echo(event):
    """
    Event subscribtion callabck, print all relevant info
    :param event:
    :return:
    """

    print(datetime.datetime.now())
    print(event)
    print("To exit use Ctrl+C!")


def sub_pull(attr, evt_type, sleep):
    ap = tango.AttributeProxy(attr)

    evt_id = ap.subscribe_event(EVENT_TYPES[evt_type], 1)

    try:
        while True:
            if not ap.is_event_queue_empty(evt_id):
                print("Extracting event")
                print("Processing event: " + str(datetime.datetime.now()))
                print("Event time: " + str(ap.get_last_event_date(evt_id)))
                events = ap.get_events(event_id=evt_id)
                print(events[0].attr_value.value)
            else:
                print("No event")
                print(datetime.datetime.now())
            time.sleep(sleep)

    except KeyboardInterrupt:
        ap.unsubscribe_event(evt_id)
        print("Unbsubscribing for %s event on attribute %s" % (evt_type, attr))


def sub_push(attr, evt_type):
    ap = tango.AttributeProxy(attr)

    evt_id = ap.subscribe_event(EVENT_TYPES[evt_type], echo)

    try:
        while True:
            pass

    except KeyboardInterrupt:
        ap.unsubscribe_event(evt_id)
        print("Unbsubscribing for %s event on attribute %s" % (evt_type, attr))


def main(attr, evt_type, push, pull):
    try:
        if push:
            sub_push(attr, evt_type)
        else:
            sub_pull(attr, evt_type, pull)

    except TypeError:
        print("Error with parsing attribute!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple  script for testing Tango events")
    parser.add_argument('attribute', help='device attribute name to test')
    parser.add_argument('event_type', choices=['periodic', 'change', 'archive'], help='type of event')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--push", action="store_true", help="Subscribe in push mode")
    group.add_argument("--pull", type=float, help="Subscribe in pull mode. Provide value of loop time")

    args = parser.parse_args()
    main(args.attribute, args.event_type, args.push, args.pull)

