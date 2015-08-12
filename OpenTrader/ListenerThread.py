# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import sys
import os
import json
from pprint import pprint, pformat
import threading
import traceback

from OTMql427.SimpleFormat import lUnFormatMessage, gRetvalToPython

class ListenerThread(threading.Thread):

    def __init__(self, sChartId, **dArgs):

        self.oLocal = threading.local()
        self._running = threading.Event()

        self.lCharts = []
        self.jLastRetval = []
        self.jLastTick = []
        self.jLastBar = []
        self.gLastTimer = []
        self.dRetvals = {}
        self.bPprint = False
        self.lHide = []

    def vPprint(self, sMsgType, sMsg=None, sPrefix="INFO: "):
        if sMsgType == 'get':
            sys.stdout.write("INFO: bPprint" +repr(self.bPprint) + "\n")
        elif sMsgType == 'set':
            self.bPprint = bool(sMsg)
        elif sMsgType in self.lHide:
            pass
        elif self.bPprint and sMsg:
            # may need more info here - chart and sMark
            sys.stdout.write(sPrefix +sMsgType +" = " +pformat(sMsg) +"\n")
        else:
            sys.stdout.write(sPrefix +sMsgType +" = " +repr(sMsg) +"\n")

    def vHide(self, sMsgType=None):
        if not sMsgType:
            sys.stdout.write("INFO: hiding " +repr(self.lHide) + "\n")
            return
        if sMsgType not in self.lHide:
            self.lHide.append(sMsgType)

    def vShow(self, sMsgType=None):
        if not sMsgType:
            sys.stdout.write("INFO: hiding " +repr(self.lHide) + "\n")
            return
        if sMsgType in self.lHide:
            self.lHide.remove(sMsgType)

    def vCallbackOnListener(self, sBody):

        sys.stdout.write("DEBUG: sBody: " +repr(sBody) +'\n')
        lArgs = lUnFormatMessage(sBody)
        sMsgType = lArgs[0]
        sChart = lArgs[1]
        sIgnore = lArgs[2] # should be a hash on the payload
        sMark = lArgs[3]
        sPayloadType = lArgs[4]
        gPayload = lArgs[4:] # overwritten below

        try:
            # sys.stdout.write("INFO: sChart: " +repr(sChart) +'\n')

            if sChart not in self.lCharts:
                # keep a list of charts that we have seen for "chart list"
                self.lCharts.append(sChart)
                
            #? FixMe: what does null come back as?
            if sMsgType == 'retval':
                # gRetvalToPython requires
                try:
                    gPayload = gRetvalToPython(lArgs)
                except Exception as e:
                    sys.stdout.write("WARN: vCallbackOnListener error decoding to Python: %s\n%r" % (str(e), sBody, ))
                    return

                self.jLastRetval = gPayload
                self.dRetvals[sMark] = gPayload
                sys.stdout.write("DEBUG: vCallbackOnListener set dRetvals: %s\n" % (sMark, ))

            elif sMsgType == 'bar':
                assert sPayloadType == 'json', \
                    sMsgType +" sPayloadType expected 'json' not " \
                    +sPayloadType +"\n" +sBody
                # can use this to find the current bid and ask
                gPayload = json.loads(lArgs[5])
                self.jLastBar = gPayload

            elif sMsgType == 'tick':
                assert sPayloadType == 'json', \
                    sMsgType +" sPayloadType expected 'json' not " \
                    +sPayloadType +"\n" +sBody
                # can use this to find the current bid and ask
                gPayload =json.loads(lArgs[5])
                self.jLastTick = gPayload

            elif sMsgType == 'timer':
                assert sPayloadType == 'json', \
                    sMsgType +" sPayloadType expected 'json'" +"\n" +sBody
                # can use this to find if we are currently connected
                gPayload = json.loads(lArgs[5])
                self.gLastTimer = gPayload
                
            elif sMsgType in ['cmd', 'exec']:
                #? why do we see outgoing messages?
                return
            else:
                sys.stdout.write("WARN: vCallbackOnListener unrecognized sMsgType: %r\n" % (sBody, ))
                return

            # may need to print more info here - chart and sMark
            if sMsgType == 'retval':
                # FixMe: not sure where these None are coming from
                if gPayload is not None:
                    # you really need sMark for retval
                    self.vPprint(sMsgType, gPayload, "INFO: [" +sMark +"] ")
            else:
                self.vPprint(sMsgType, gPayload)
        except Exception as e:
            sys.stderr.write(traceback.format_exc(10) +"\n")

