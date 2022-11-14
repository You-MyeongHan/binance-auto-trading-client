from PyQt5.QtWidgets import QApplication, QGraphicsView, QGridLayout
import sys
import finplot as fplt
import ccxt
import pandas as pd
fplt.candle_bull_color = "#FF0000"
fplt.candle_bull_body_color = "#FF0000" 
fplt.candle_bear_color = "#0000FF"


class MyWindow(QGraphicsView):
    def __init__(self, ticker):
        super().__init__()

        self.setWindowTitle("QGraphicsView")
        layout = QGridLayout()
        self.setLayout(layout)
        self.resize(800, 300)

        # ax
        ax = fplt.create_plot(init_zoom_periods=100)
        self.axs = [ax] # finplot requres this property
        layout.addWidget(ax.vb.win, 0, 0)

        binance = ccxt.binance()
        ohlcv = binance.fetch_ohlcv(symbol=ticker, timeframe='1h')
        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df.set_index('datetime', inplace=True)
        fplt.candlestick_ochl(df[['open', 'close', 'high', 'low']])
        fplt.show(qt_exec=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow("BTC/USDT") 
    win.show()
    app.exec_()