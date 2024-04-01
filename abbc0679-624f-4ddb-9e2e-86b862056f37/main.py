from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Asset
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the stock symbols in a hypothetical universe.
        # In a real-world scenario, this might be dynamically generated to include stocks matching certain criteria.
        self.tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]  # Placeholder tickers, adjust based on actual strategy requirements
        self.purchase_price = None
        self.stock_held = None

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "15min"  # Check every 15 minutes to match the "recent high" requirement.

    @property
    def data(self):
        # No additional data requested in this strategy example
        return []

    def run(self, data):
        allocation_dict = {}

        # If we are holding a stock, check if the target sell conditions are met.
        if self.stock_held:
            current_price = data["ohlcv"][-1][self.stock_held]["close"]
            change_percent = (current_price - self.purchase_price) / self.purchase_price * 100

            if change_percent >= 11 or change_percent <= -7:
                log(f"Selling {self.stock_held} at {current_price} for a {change_percent}% change")
                allocation_dict[self.stock_held] = 0  # Sell the stock
                self.stock_held = None
                self.purchase_price = None
            else:
                log(f"Holding {self.stock_held}. Current change: {change_percent}%")
                allocation_dict[self.stock_held] = 1  # Keep holding with 100% allocation
        else:
            for ticker in self.tickers:
                # Check for stocks within the price range and up over 15% for the day
                recent_data = data["ohlcv"][-1][ticker]
                volume = recent_data["volume"]
                close_price = recent_data["close"]
                open_price = recent_data["open"]
                high_of_day = max(record[ticker]["high"] for record in data["ohlcv"])
                current_change = (close_price - open_price) / open_price * 100

                if 1 < close_price < 5 and current_change > 15 and volume > 10_000_000 and close_price == high_of_day:
                    log(f"Buying {ticker} at {close_price} with a change of {current_change}% and volume {volume}")
                    allocation_dict[ticker] = 1  # Allocate 100% capital to this stock
                    self.stock_held = ticker
                    self.purchase_price = close_price
                    break  # Buy only one stock at a time
            else:
                log("No suitable stock meets the criteria at this time.")  # No stock was found to buy

        # If no stock is being held or bought, the allocation stays empty
        return TargetAllocation(allocation_dict)