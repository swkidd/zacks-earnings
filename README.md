# zacks-earnings
Get earnings releases from zacks.com/earnings/earnings-reports by date  
```python
>>> ZacksEarnings.earnings_by_date(parser.parse('Aug 12, 2017'))
   Symbol                                Company Report Time  Estimate Reported Surprise  Current Price  Price % Change  Unnamed: 8
0    ABCP                           AmBase Corp.       15:41       NaN    -0.03      NaN           0.32            0.00         NaN
1    ADMA                     ADMA Biologics Inc       16:22     -0.42    -0.55   -30.95           2.12            2.42         NaN
2    AIKI                     AIkido Pharma Inc.       18:00       NaN    -1.61      NaN           1.38            8.66         NaN
3     AIT  Applied Industrial Technologies, Inc.       06:35      0.77     0.78     1.30          93.16            1.43         NaN
4    ARCT    Arcturus Therapeutics Holdings Inc.       08:05     -0.91    -0.91      NaN          46.40           -4.01         NaN
..    ...                                    ...         ...       ...      ...      ...            ...             ...         ...
94  VLRXQ               Valeritas Holdings, Inc.       08:01    -33.40   -36.60    -9.58           0.02            0.00         NaN
95   VRDN            Viridian Therapeutics, Inc.       16:11     -7.05    -5.10    27.66          17.98            0.22         NaN
96   XAIR                       Beyond Air, Inc.       16:07       NaN    -0.46      NaN           5.88           -2.33         NaN
97    XIN             Xinyuan Real Estate Co Ltd       06:10       NaN     0.14      NaN           2.97           -0.67         NaN
98   ZNOG                     Zion Oil & Gas Inc       05:03       NaN    -0.10      NaN           0.73            1.37         NaN
[99 rows x 9 columns]
```

Get the zacks estimated next earnings date for a symbol  
```python
>>> ZacksEarnings.get_next_earnings_estimate('aapl')
[datetime.datetime(2021, 4, 29, 0, 0)]
```
