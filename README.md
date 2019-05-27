# StockAnalyser

## Fetch stock data:
./script/fetch.py

## Calculate indicators:
1. macd: ./script/macd.py
2. kdj:  ./script/kdj.py
3. boll: ./script/boll.py

## Generate new DAF:
1. cd ./csrc
2. ./genDAF.py <daf_name> ,it will generate a directory named by <daf_name>
3. cd ./<daf_name>, there is a DAF_<daf_name>.cpp there, you can write buyChecker() and sellChecker() functions, also you should choose which indicators are used in init().
4. make <DEBUG=1>

## Run analyser:
1. ./script/analyser.py <daf_name> 2018-01-01 2018-12-31 mask=7
2. use chart to display the result, ./script/chart.py ./log/macd_2018-01-01_2018-12-31_7_1.log                                                                                                            
