#ifndef DAF_H
#define DAF_H

/********************************************************************
 * DAF.h: define DAF                                                *
 *                                            2018 Hui              *
 ********************************************************************/

#include "stdio.h"
#include "math.h"
#include "buyer.h"
#include "string.h"
#include "assert.h"
#include "pthread.h"
#include "sys/stat.h"
#include "fileLoc.h"
#include <omp.h>
#include "sys/time.h"


//shenzhen (000001, 002940)
//cyb      (300000, 300760)
//shanghai (600000, 603999)

#define LOG_LENGTH                  1024*1024
#define ALL_STOCK_NUM               604000
#define DEBUG_OUTPUT                //printf
//all kinds fee payed when trading
#define FEE_STOCK_COMPANY           (2.5/10000)
#define FEE_STOCK_COMPANY_BASIC     5
#define FEE_CHANGE                  0.06
#define FEE_PRINT                   (0.1/100)

//indicator type
#define INDICATOR_MACD              1
#define INDICATOR_KDJ               1 << 1
#define INDICATOR_BOLL              1 << 2

//trade macro definitions:
#define FIX_CONDITION(x)            if ((x.next.close / x.trade.close > 1.095) && (x.next.open == x.next.high)) return false;
#define SELL_FIX_CONDITION(x)       if((x.next.close / x.trade.close < 0.905) && (x.next.open == x.next.low)) return NULL; 
#define CHECK_MARKET_MASK(mask, sm0, sm1)   switch(mask) \
                                            {\
                                            case 1:\
                                                sm0 = 0;\
                                                sm1 = 1;\
                                                break;\
                                            case 2:\
                                                sm0 = 1;\
                                                sm1 = 2;\
                                                break;\
                                            case 4:\
                                                sm0 = 2;\
                                                sm1 = 3;\
                                                break;\
                                            case 3:\
                                                sm0 = 0;\
                                                sm1 = 2;\
                                                break;\
                                            case 5:\
                                            case 7:\
                                                sm0 = 0;\
                                                sm1 = 3;\
                                                break;\
                                            case 6:\
                                                sm0 = 1;\
                                                sm1 = 3;\
                                                break;\
                                            default:\
                                                sm0 = 0;\
                                                sm1 = 3;\
                                            }

#define DAF_NAME_BASIC "basic"
typedef struct day_trade
{
    int    index;
    long   date;
    char   dateStr[15];
    float  open;
    float  high;
    float  close;
    float  low;
    unsigned long  volume;
    unsigned long  amount;
}dayTrade;

typedef struct day_trade_list
{
    dayTrade trade;
    dayTrade pre;
    dayTrade next;
}dayTradeList;

typedef struct info_buffer
{
    int   offset;
    char* content;
    int   length;
}infoBuffer;

class DAF
{
public:
    char           _name[64];               //DAF name
    int            _indexList[3][2];        //stock index list
    int            _hold;                   //the stock index current hold
    dayTradeList   _buy;                    //information of buy
    dayTradeList   _sell;                   //information of sell
    dayTradeList   _current;                //current information about trade
    long           _money;                  //total money
    char*          _logString;              //log
    float          _score[ALL_STOCK_NUM];   //score for every stock
    int            _marketMask;             //to determine which markets are involved
    char           _dateStr[20];            //current date string
    float          _fee;                    //trade fee
    bool           _init;                   //whether initialized
    unsigned int   _indicator;              //to determine which indicators are used

    infoBuffer*    _tradeInfo;              //to store trade information
    infoBuffer*    _macdInfo;               //to store MACD information
    infoBuffer*    _kdjInfo;                //to store KDJ information
    infoBuffer*    _bollInfo;               //to store BOLL information
private:
    void initIndicator(void);
public:
    DAF()
    {
        strcpy(_name, DAF_NAME_BASIC);
        _indexList[0][0] = 1;
        _indexList[0][1] = 2940;
        _indexList[1][0] = 300000;
        _indexList[1][1] = 300760;
        _indexList[2][0] = 600000;
        _indexList[2][1] = 603999;
        _hold = 0;
        memset(&_buy, 0, sizeof(_buy));
        memset(&_sell, 0, sizeof(_sell));
        memset(&_current, 0, sizeof(_current));
        _money = 0;
        _logString = (char*)malloc(LOG_LENGTH);
        memset(_logString, 0, LOG_LENGTH);
        memset(_score, 0, sizeof(_score));
        _marketMask = 7;                                   // default for all markets
        memset(_dateStr, 0, sizeof(_dateStr));             // to store sell date
        _fee = 0;
        _indicator = 0;

        _tradeInfo = NULL;
        _macdInfo = NULL;
        _kdjInfo = NULL;
        _bollInfo = NULL;
    }

    DAF(int stockMarket)
    {
        _marketMask = stockMarket;
    }

    ~DAF(){}

    virtual void init(){}
    virtual int buy(char* date);
    virtual char* sell(char* date);
    virtual bool sellChecker(char* date, int index, dayTradeList* tradeList)
    {
        return false;
    }
    virtual bool buyChecker(char* date, int index, dayTradeList* tradeList)
    {
        return false;
    }

    void logfile(char* appendStr);
    long profit(long money);
    dayTradeList getDayTradeByBuf(int index, char* date);
    bool getMacdValueByBuf(int index, char* date, float* macd, float* dif, float* dea);
    int getKDJValueByBuf(int index, char* date, float* K, float* D, float* J, int num);
    int getBOLLValueByBuf(int index, char* date, float* BOLL, float* UB, float* LB, int num);
};

#endif
