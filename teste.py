import sys
import requests
import sqlite3
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit

# Constants
API_KEY = '2GLRRNE06HF2GIPD'
BASE_URL = 'https://www.alphavantage.co/query'
DATABASE_FILE = 'stocks_data.db'


# Helper function to create database and tables if not exists
def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            symbol TEXT PRIMARY KEY,
            latest_close REAL,
            sma_5min REAL,
            recommendation TEXT
        )
    ''')
    conn.commit()
    conn.close()


class FinancialDataFetcher(QtCore.QThread):
    data_fetched = QtCore.pyqtSignal(str, dict)
    error_occurred = QtCore.pyqtSignal(str)

    def __init__(self, symbols):
        super().__init__()
        self.symbols = symbols

    def run(self):
        for symbol in self.symbols:
            try:
                response = requests.get(BASE_URL, params={
                    'function': 'TIME_SERIES_INTRADAY',
                    'symbol': symbol,
                    'interval': '5min',
                    'apikey': API_KEY
                })
                data = response.json()
                if 'Time Series (5min)' in data:
                    self.data_fetched.emit(symbol, data['Time Series (5min)'])
                else:
                    self.error_occurred.emit(f'Error fetching data for {symbol}')
            except Exception as e:
                self.error_occurred.emit(f'Exception occurred for {symbol}: {str(e)}')


class FinancialDataAnalyzer(QtCore.QThread):
    analysis_result = QtCore.pyqtSignal(str)

    def __init__(self, symbol, data):
        super().__init__()
        self.symbol = symbol
        self.data = data

    def run(self):
        if not self.data:
            self.analysis_result.emit(f'No data to analyze for {self.symbol}')
            return

        # Calculate 5-Minute SMA
        timestamps = list(self.data.keys())
        if len(timestamps) < 5:
            self.analysis_result.emit(f'Not enough data to calculate SMA for {self.symbol}')
            return

        recent_closes = [float(self.data[timestamp]['4. close']) for timestamp in timestamps[:5]]
        sma_5min = sum(recent_closes) / 5
        latest_close = float(self.data[timestamps[0]]['4. close'])

        recommendation = "Hold"
        if latest_close > sma_5min:
            recommendation = "Buy"
        elif latest_close < sma_5min:
            recommendation = "Sell"

        self.analysis_result.emit(f'Symbol: {self.symbol}\n'
                                  f'Latest Close: R${latest_close:.2f}\n'
                                  f'5-Minute SMA: R${sma_5min:.2f}\n'
                                  f'Recommendation: {recommendation}')

        # Save to database
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO stocks (symbol, latest_close, sma_5min, recommendation)
            VALUES (?, ?, ?, ?)
        ''', (self.symbol, latest_close, sma_5min, recommendation))
        conn.commit()
        conn.close()


class FinancialApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Data Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.symbol_input = QLineEdit(self)
        self.symbol_input.setPlaceholderText("Enter stock symbols (comma separated) or leave blank for top 20")
        self.layout.addWidget(self.symbol_input)

        self.investment_input = QLineEdit(self)
        self.investment_input.setPlaceholderText("Enter amount to invest (in BRL)")
        self.layout.addWidget(self.investment_input)

        self.fetch_button = QPushButton("Fetch Data", self)
        self.fetch_button.clicked.connect(self.fetch_data)
        self.layout.addWidget(self.fetch_button)

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.last_update_label = QLabel("Last Update: Not yet updated")
        self.layout.addWidget(self.last_update_label)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(300000)  # Update every 5 minutes

        self.symbols = []
        self.investment_amount = 0.0
        self.data_fetcher = None
        self.data_analyzer = None

        # Initialize database
        initialize_database()

    def fetch_data(self):
        self.symbols = self.symbol_input.text().strip().upper().split(',')
        self.investment_amount = float(self.investment_input.text().strip() or 0)

        if not self.symbols or not self.symbols[0]:
            self.symbols = self.get_top_stocks()

        if not self.symbols:
            self.log("No symbols to fetch data for.")
            return

        self.log(f"Fetching data for symbols: {', '.join(self.symbols)}")
        self.data_fetcher = FinancialDataFetcher(self.symbols)
        self.data_fetcher.data_fetched.connect(self.process_data)
        self.data_fetcher.error_occurred.connect(self.log)
        self.data_fetcher.start()

    def get_top_stocks(self):
        # Define a method to get the top stocks; for now, we'll use a placeholder
        return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'BABA', 'NVDA', 'CRM']

    def process_data(self, symbol, data):
        self.log(f"Data fetched for {symbol}. Analyzing...")
        self.data_analyzer = FinancialDataAnalyzer(symbol, data)
        self.data_analyzer.analysis_result.connect(self.log_analysis)
        self.data_analyzer.start()

        self.last_update_label.setText(f"Last Update: {QtCore.QDateTime.currentDateTime().toString()}")

    def log_analysis(self, result):
        self.log(result)
        self.recommend_buying()

    def recommend_buying(self):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocks')
        stocks = cursor.fetchall()
        conn.close()

        recommendations = []
        for stock in stocks:
            symbol, latest_close, sma_5min, recommendation = stock
            if recommendation == "Buy":
                amount_to_invest = self.investment_amount
                quantity = amount_to_invest // latest_close
                recommendations.append(f"Symbol: {symbol}\n"
                                       f"Recommended to Buy: {quantity} shares\n"
                                       f"Price per Share: R${latest_close:.2f}\n"
                                       f"Total Investment: R${latest_close * quantity:.2f}\n")

        if recommendations:
            self.log("Recommendations based on your investment amount:\n" + "\n".join(recommendations))
        else:
            self.log("No suitable recommendations based on current data.")

    def log(self, message):
        self.log_text.append(message)

    def update_data(self):
        self.fetch_data()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FinancialApp()
    window.show()
    sys.exit(app.exec_())
