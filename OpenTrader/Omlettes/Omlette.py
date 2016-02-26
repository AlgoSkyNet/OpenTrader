# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""

   ``PyTables`` will show a ``NaturalNameWarning`` if a  column name
   cannot be used as an attribute selector. Generally identifiers that
   have spaces, start with numbers, or ``_``, or have ``-`` embedded are not considered
   *natural*. These types of identifiers cannot be used in a ``where`` clause
   and are generally a bad idea.

"""

import sys
import os
from collections import OrderedDict
import pandas

from OpenTrader.PandasMt4 import oReadMt4Csv

class Omlette(object):
    __fOmleteVersion__ = 1.0
    
    def __init__(self, sHdfStore="", oFd=sys.stdout):
        self.oHdfStore = None
        self.oFd = oFd
        if sHdfStore:
            # ugly - active
            self.oHdfStore = pandas.HDFStore(sHdfStore, mode='w')
            self.oFd.write("INFO: hdf store" +self.oHdfStore.filename +'\n')

        self.oRecipe = None
        self.oChefModule = None

    def oAddHdfStore(self, sHdfStore):
        if os.path.isabs(sHdfStore):
            assert os.path.isdir(os.path.dirname(sHdfStore)), \
                   "ERROR: directory not found: " +sHdfStore
        self.oHdfStore = pandas.HDFStore(sHdfStore, mode='w')
        self.oFd.write("INFO: hdf store: " +self.oHdfStore.filename +'\n')
        return self.oHdfStore
            
    def oRestore(self, sHdfStore):
        assert os.path.exists(sHdfStore)
        # FixMe:
        self.oHdfStore = None
        return self.oHdfStore
        
    # Is this an Omlette method? its generic and the use of self is tangential
    # It is because it adds components to the HDF fuke, which is the omlette.
    def dGetFeedFrame(self, sCsvFile, sTimeFrame, sSymbol, sYear):
        dFeedParams = OrderedDict(sTimeFrame=sTimeFrame, sSymbol=sSymbol, sYear=sYear)
        # PandasMt4.dDF_OHLC[sKey = sSymbol + sTimeFrame + sYear]
        dFeedParams['mFeedOhlc'] = oReadMt4Csv(sCsvFile, **dFeedParams)
        dFeedParams['open_label'] = 'O'
        dFeedParams['close_label'] = 'C'
        dFeedParams['sKey'] = sSymbol + sTimeFrame + sYear
        dFeedParams['sCsvFile'] = sCsvFile

        self.vAppendHdf('feed/mt4/' +dFeedParams['sKey'],
                        dFeedParams['mFeedOhlc'])
        dMetadata = dFeedParams.copy()
        del dMetadata['mFeedOhlc']        
        self.vSetMetadataHdf('feed/mt4/' +dFeedParams['sKey'], dMetadata)
        self.vSetTitleHdf('feed/mt4', 'Mt4')
        self.vSetTitleHdf('feed', 'Feeds')
        return dFeedParams
    
    def oAddRecipe(self, sRecipe):
        if False:
            OpenTraderPkg = __import__('OpenTrader.Omlettes.'+sRecipe)
            OmlettesPkg = getattr(OpenTraderPkg, 'Omlettes')
            RecipeModule = getattr(OmlettesPkg, sRecipe)
        else:
            RecipeModule = __import__(sRecipe)
        RecipeKlass = getattr(RecipeModule, sRecipe)
        self.oRecipe = RecipeKlass()
        self.oRecipe.sName = sRecipe
        self.oRecipe.sFile = RecipeModule.__file__
        self.oRecipe.oOm = self
        return self.oRecipe
    
    def oAddChef(self, sChef):
        if False:
            OpenTraderPkg = __import__('OpenTrader.Omlettes.'+sChef)
            OmlettesPkg = getattr(OpenTraderPkg, 'Omlettes')
            self.oChefModule = __import__(sChef)
        else:
            self.oChefModule = getattr(OmlettesPkg, sChef)
        # self.sChef = sChef
        # FixMe: eliminate
        self.oChefModule.sChef = sChef
        self.oChefModule.sName = sChef
        return self.oChefModule
    
    def dMakeChefsParams(self, **dKw):
        self.dChefsParams = OrderedDict(**dKw)
        return self.dChefsParams
    
    def vSetTitleHdf(self, sKey, sData):
        oHdfStore = self.oHdfStore
        if oHdfStore is None: return
        self.oHdfStore.get_node(sKey)._g_settitle(sData)

    def vSetMetadataHdf(self, sKey, gData):
        oHdfStore = self.oHdfStore
        if oHdfStore is None: return
        self.vAppendHdf(sKey, None, gData)

    def vAppendHdf(self, sKey, gData, gMetaData=None):
        oHdfStore = self.oHdfStore
        if oHdfStore is None: return
        
        if gData is None:
            # we need to check if the key exists
            pass
            # drop through
        # assert sCat in ['recipe', 'feed'], "ERROR: unrecognized category: " +sCat
        elif type(gData) in [pandas.Series, pandas.DataFrame, pandas.Panel]:
            self.oFd.write("INFO: HDF putting " +sKey +'\n')
            oHdfStore.put('/' +sKey, gData,
                          format='table',
                          data_columns=True)
            oHdfStore.flush()
        else:
            self.oFd.write("ERROR: unsupported datatype for %s: %r \n" % \
                           (sKey, type(gData),))
            return
        
        if gMetaData is None:
            return
        if type(gMetaData) in [dict, OrderedDict]:
            # o = getattr(getattr(oHdfStore.root, sCat), sInst)
            o = oHdfStore.get_node('/'+sKey)
            o._v_attrs.metadata = [gMetaData]
            oHdfStore.flush()

    def vClose(self):
        if self.oHdfStore is None: return
        if False:
            self.oFd.write("INFO: closing hdf " +repr(self.oHdfStore) +'\n')
        self.oHdfStore.close()
        self.oHdfStore = None

def iMain():
    """
    Read an hdf file generated by us to make sure
    we can recover its content and structure.
    Give the name of an hdf5 file as a command-line argument.
    """
    assert sys.argv, __doc__
    sFile = sys.argv[1]
    assert os.path.isfile(sFile)
    oHdfStore = pandas.HDFStore(sFile, mode='r')
    print oHdfStore.groups()
    # bug - no return value
    # oSignals = pandas.read_hdf(oHdfStore, '/servings/signals')
    mSignals = oHdfStore.select('/recipe/servings/mSignals', auto_close=False)    
    print mSignals
    print oHdfStore.get_node('/recipe')._v_attrs.metadata[0]['sUrl']
    
if __name__ == '__main__':
    iMain()
