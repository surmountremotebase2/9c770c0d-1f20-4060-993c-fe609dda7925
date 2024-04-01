from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OptionChain, OHLCV
from surmount.logging import log

class TradingStrategy(Strategy):

    def __init__(self):
        # SPY is the ticker symbol for S&P 500 ETF Trust
        # The strategy focuses on trading ODTE (One Day to Expiry) options for SPY
        self.ticker = "SPY"

    @property
    def interval(self):
        # The strategy checks for trading opportunities with each new daily data
        return "1day"

    @property
    def assets(self):
        # Only interested in SPY for this strategy
        return [self.ticker]

    @property
    def data(self):
        # Using OptionChain to get data on available options and OHLCV for the underlying asset's price
        return [OptionChain(self.ticker), OHLCV(self.ticker)]

    def run(self, data):
        allocation_dict = {}
        # Retrieve the latest closing price of SPY
        current_price = data["ohlcv"][-1][self.ticker]["close"]

        # Retrieve the option chains for SPY
        options = data["option_chain"][self.ticker]

        # Loop through the options to find ODTE calls or puts that are within one cent of the strike price
        for option in options:
            if option["daysToExpiry"] == 1 and abs(option["strike"] - current_price) <= 0.01:
                # When an option meets the criteria, we decide to trade it
                # The key for the allocation dictionary is a tuple ([OPTION_TYPE],[TICKER],[EXPIRY_DATE],[STRIKE_PRICE])
                option_key = (option["type"], self.ticker, option["expiryDate"], option["strike"])
                
                # Determine entry price based on the option type
                entry_price = option["askPrice"] if option["type"] == "call" else option["bidPrice"]

                # We buy the option by setting its target allocation. The strategy here is simplified
                # and assumes a fixed allocation which should be adjusted according to account size and risk management
                allocation_dict[option_key] = 1.0  # this is a placeholder to indicate a 'buy'

                # Add logic to sell at a 10% increase or decrease in the option's price
                # NOTE: Actual implementation of monitoring for a 10% price change should be
                # handled by keeping track of the entry prices and comparing current prices
                # But for simplicity, the example does not provide a direct way to check price movement and perform sells
                
                log(f"Buying {option['type']} option for SPY at strike {option['strike']} with expiry {option['expiryDate']}")
                break  # Assume buying only one option for simplicity

        return TargetAllocation(allocation_dict)