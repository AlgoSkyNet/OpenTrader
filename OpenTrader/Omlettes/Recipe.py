# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""

   ``PyTables`` will show a ``NaturalNameWarning`` if a  column name
   cannot be used as an attribute selector. Generally identifiers that
   have spaces, start with numbers, or ``_``, or have ``-`` embedded are not considered
   *natural*. These types of identifiers cannot be used in a ``where`` clause
   and are generally a bad idea.

"""
import sys, os
import pandas
from collections import OrderedDict
from configobj import ConfigObj
from PybacktestChef import mExtractFrame

class Recipe(object):
    
    __fRecipeVersion__ = 1.0

    def __init__(self, oOm=None, oFd=sys.stdout):
        self.oOm = oOm
        self.oFd = oFd
        self.oConfigObj = None
        self.sName = ""
        self.sFile = ""
        self.oOm = None
        
    def zReadIniFile(self):
        if self.sIniFile == "":
            self.oFd.write("INFO: No INI file defined" +'\n')
        else:
            sIniFile = self.sIniFile
            if not os.path.isabs(sIniFile):
                sIniFile = os.path.join(os.path.dirname(__file__), self.sIniFile)
            if not os.path.isfile(sIniFile):
                self.zWriteIniFile()
            if os.path.isfile(sIniFile) and not self.oConfigObj:
                oConfigObj = ConfigObj(sIniFile, unrepr=True)
                self.oFd.write("INFO: Read INI file: " +oConfigObj.filename +'\n')
                self.oConfigObj = oConfigObj
                for sKey, gValue in oConfigObj[self.sName].items():
                    setattr(self, sKey, gValue)
                self.lRequiredFeeds = [oConfigObj[s] for s in
                                       self.lRequiredFeedParams]
                self.lRequiredDishes = [oConfigObj[s] for s in
                                       self.lRequiredDishesParams]
                # eliminate
                self.lRequiredIngredients = []
                for sElt in self.lRequiredIngredients:
                    self.lRequiredDishes += [sElt]
                    for sKey in oConfigObj[sElt].keys():
                        if sKey not in self.lRequiredIngredients:
                            self.lRequiredIngredients += [sKey]
                                             
                
    def zWriteIniFile(self):
        if self.sIniFile != "":
            sIniFile = self.sIniFile
            if not os.path.isabs(sIniFile):
                sIniFile = os.path.join(os.path.dirname(__file__), self.sIniFile)
            if not os.path.isfile(sIniFile):
                oConfigObj = ConfigObj(unrepr=True)
                oConfigObj.filename = sIniFile
                oConfigObj[self.sName] = dict(fRecipeVersion= self.__fRecipeVersion__)
                
                lKeys = []
                for dElt in self.lRequiredFeeds:
                    for sKey, dVal in dElt.items():
                        oConfigObj[sKey] = dVal
                        lKeys += [sKey]
                self.lRequiredFeedParams = lKeys
                #? duplication
                oConfigObj[self.sName]['lRequiredFeedParams'] = self.lRequiredFeedParams
                
                self.lRequiredDishesParams = []
                self.lRequiredIngredientsParams = []
                for dElt in self.lRequiredIngredients:
                    for sKey, dVal in dElt.items():
                        oConfigObj[sKey] = dVal
                        self.lRequiredDishesParams += [sKey]
                        for sKey1 in dVal.keys():
                            if sKey1 not in self.lRequiredIngredientsParams:
                                self.lRequiredIngredientsParams += [sKey1]
                oConfigObj[self.sName]['lRequiredDishesParams'] = self.lRequiredDishesParams
                oConfigObj[self.sName]['lRequiredIngredientsParams'] = self.lRequiredIngredientsParams
                
                oConfigObj.write()
                self.oFd.write("INFO: Wrote INI file: " +oConfigObj.filename +'\n')
                
    def dRecipeParams(self):
        return OrderedDict(sName=self.sName,
                           sUrl='file://' +self.sFile)
        
    def vCheckRequiredFeeds(self, dFeeds):
        for sKey in self.lRequiredFeedParams:
            assert sKey in dFeeds, \
                   "ERROR: %s not found in %r" % (sKey, dFeeds)
                ## if hasattr(d[sKey], 'sPandasType'):
                ##     oT = getattr(pandas, d[sKey]['sPandasType'])
                ##     assert isinstance(dFeeds[sKey], oT), \
                ##            "ERROR: %s not of type %r" % (sKey, oT)
                ## if hasattr(d[sKey], 'lNames'):
                ##     # FixMe:
                ##     pass
                
    def vCheckRequiredDishes(self, dRecipeParams):
        # I'm confused - was lIngredients ; is rShortMa rLongMa or sName sUrl?
        return
        assert hasattr(self, 'lRequiredIngredientsParams')
        for sKey in self.lRequiredIngredientsParams:
            assert sKey in dRecipeParams, \
                   "ERROR: %s not found in %r" % (sKey, dRecipeParams)

    def mSignals(self, oBt):
        assert oBt.dDataDict
        for sKey in oBt._lSignalFieldsExt:
            # signals must be in the dDataDict or we cant run
            assert sKey in oBt.dDataDict
        m = mExtractFrame(oBt.dDataDict, oBt._lSignalFieldsExt,
                          oBt._lSignalFieldsInt)
        assert m is not None
        return m.fillna(value=False)
    
    # taken from pybacktest.parts.signals_to_positions
    def rPositions(self, oBt, init_pos=0,
                 mask=('Buy', 'Sell', 'Short', 'Cover')):
        # we need a portfolio manager
        """
        Translate signal dataframe into positions series (trade prices aren't
        specified.
        WARNING: In production, override default zero value in init_pos with
        extreme caution.
        """
        mSignals = oBt.signals
        long_en, long_ex, short_en, short_ex = mask
        pos = init_pos
        rPosition = pandas.Series(0.0, index=mSignals.index)
        for t, sig in mSignals.iterrows():
            # check exit mSignals
            if pos != 0:  # if in position
                if pos > 0 and sig[long_ex]:  # if exit long signal
                    pos -= sig[long_ex]
                elif pos < 0 and sig[short_ex]:  # if exit short signal
                    pos += sig[short_ex]
            # check entry (possibly right after exit)
            if pos == 0:
                if sig[long_en]:
                    pos += sig[long_en]
                elif sig[short_en]:
                    pos -= sig[short_en]
            rPosition[t] = pos
        return rPosition[rPosition != rPosition.shift()]

    # taken from pybacktest.backtest.trades
    def mTrades(self, oBt):
        #? , 
        rPositions = oBt.positions
        mSignals = oBt.signals
        rTradePrice = oBt.trade_price
        p = rPositions.reindex(
            mSignals.index).ffill().shift().fillna(value=0)
        p = p[p != p.shift()]
        assert p.index.tz == rTradePrice.index.tz, \
               "Cant operate on signals and prices " + \
               "indexed as of different timezones"
        mTrades = pandas.DataFrame({'pos': p})
        mTrades['price'] = rTradePrice
        mTrades = mTrades.dropna()
        mTrades['vol'] = mTrades.pos.diff()
        # timestamp ('pos', 'price', 'vol')
        return mTrades.dropna()

    # taken from pybacktest.backtest.trades_to_equity
    def rEquity(self, oBt):
        """
        Convert trades dataframe (cols [vol, price, pos]) to equity diff series
        """
        mTrades = oBt.trades

        def _cmp_fn(x):
            if x > 0:
                return 1
            elif x < 0:
                return -1
            else:
                return 0

        rPositionsSign = mTrades.pos.apply(_cmp_fn)
        closepoint = rPositionsSign != rPositionsSign.shift()
        e = (mTrades.vol * mTrades.price).cumsum()[closepoint] - \
            (mTrades.pos * mTrades.price)[closepoint]
        e = e.diff()
        e = e.reindex(mTrades.index).fillna(value=0)
        e[e != 0] *= -1
        return e
