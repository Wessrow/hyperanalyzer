#!/usr/bin/python3

"""
The purpose of this code is to scrape the Hypercharts API
Code written by Gustav Larsson
"""

import os
import sys
import requests
from logging_handler import logger

def load_api_key():
    """
    Helper function to load API-key.
    """

    api_key = os.environ.get("API_KEY")

    return api_key

def format_logs(level, message_type, message):
    """
    Helper function to format error messages
    """

    data = {"type": message_type,
                "message": message
    }

    logger.log(level, data)

class HyperAPI:
    """
    Class to work with Hypercharts API.
    """

    def __init__(self, api_key):
        """
        Constructor for the class, sets variables for further use.
        """

        self.api_key = api_key
        self.base_url = "https://api.hypercharts.co/v1/"

    def _req(self, resource, symbol=None):
        """
        Private helper function for API-calls.
        """

        params = f"?symbol={symbol}&apiKey={self.api_key}"

        response = requests.get(f"{self.base_url}/{resource}{params}")

        if response.status_code == 200:
            format_logs(20, response.status_code, "Success")

            result = response

        elif response.status_code == 404:

            format_logs(40, response.status_code, f"Resource '{resource}' does not exist")

            sys.exit(1)

        elif response.status_code == 400:

            error_message = response.json()["error"]
            format_logs(40, response.status_code, error_message)

            sys.exit(1)

        return result

    def _parse_financials(self, symbol):
        """
        Private helper function to parse relevant financial info
        """

        relevant_info = {}

        raw_info = self._req(resource="financials", symbol=symbol).json()

        for quarter in raw_info["financials"]:
            try:
                relevant_info.update({
                    quarter["Quarter"]:{
                        "Stock Price": quarter["Stock Price"],
                        "Net Income": quarter["Net Income"],
                        "Outstanding Shares": quarter["Outstanding Shares"],
                    }
                })
                format_logs(10, "ParsedQuarter", f"{symbol} - {quarter['Quarter']}")
            except KeyError as error:
                format_logs(40, "KeyError", f"symbol: {symbol} - key: {error}")
                break

        format_logs(20, "ParsedFinancials", symbol)
        return relevant_info

    @staticmethod
    def _calc_eps(income, shares):
        """
        Small helper function to calculate earnings per share
        """

        try:
            eps = round(int(income) / int(shares), 3)
            format_logs(10, "CalculatedEPS", eps)

        except TypeError as error:
            format_logs(40, "CalcError", error)

        return eps

    def eps_per_quarter(self, symbol):
        """
        Returns calculated EPS per quarter available
        """

        data = self._parse_financials(symbol)
        parsed_eps = {}

        for quarter in data:

            eps = self._calc_eps(data[quarter]["Net Income"], data[quarter]["Outstanding Shares"])
            parsed_eps.update({quarter:eps})

        format_logs(20, "ParsedEPS", symbol)
        return parsed_eps

if __name__ == "__main__":

    testObj = HyperAPI(load_api_key())

    # financials = testObj._req(resource="financials", symbol="aapl").json()
    # financials = testObj._parse_financials(symbol="amzn")

    # print(financials["financials"])
    # print(json.dumps(financials, indent=2))

    testObj.eps_per_quarter("aapl")
