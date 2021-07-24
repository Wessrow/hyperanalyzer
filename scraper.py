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

    info = {"type": message_type,
                "message": message
    }

    logger.log(level, info)

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

        relevant_info = {"symbol":symbol,
                        "data":[]}

        raw_info = self._req(resource="financials", symbol=symbol).json()

        for quarter in raw_info["financials"]:
            try:
                relevant_info["data"].append({
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

        # import json
        # print(json.dumps(relevant_info, indent=2))

        return relevant_info

    @staticmethod
    def _calc_eps(income, shares):
        """
        Helper function to calculate earnings per share
        """

        try:
            eps = round(float(income) / float(shares), 3)
            format_logs(10, "CalculatedEPS", eps)

            return eps

        except TypeError as error:
            format_logs(40, "TypeError", error)
            return None

    @staticmethod
    def _calc_pe(stock_price, eps):
        """
        Helper function to calculate price per earnings
        """

        # print(stock_price, eps, type(stock_price), type(eps))

        try:
            pe_ratio = round(float(stock_price) / float(eps))
            format_logs(10, "CalculatedPE", pe_ratio)

            return pe_ratio

        except TypeError as error:
            format_logs(40, "TypeError", error)
            return  None

    def eps_per_quarter(self, data):
        """
        Returns calculated EPS per quarter available
        """

        parsed_eps = {"symbol":data["symbol"],
                    "data":[]}

        for entry in data["data"]:
            for item in entry.items():
                eps = self._calc_eps(item[1]["Net Income"], item[1]["Outstanding Shares"])
                parsed_eps["data"].append({item[0]:eps})

        # import json
        # print(json.dumps(parsed_eps, indent=2))

        format_logs(20, "ParsedEPS", data["symbol"])
        return parsed_eps

    def pe_per_quarter(self, data):
        """
        Returns calculated PE ratio per quarter available
        """

        parsed_pe = {"symbol":data["symbol"],
                    "data":[]}

        eps = self.eps_per_quarter(data)

        for entry in zip(data["data"], eps["data"]):
            for quarter in entry[0]:
                
                stock_price = entry[0][quarter]["Stock Price"]
                eps = entry[1][quarter]

                # format_logs(10, "MathCheck", f"{stock_price}, {eps}")

                if isinstance(stock_price, float) and isinstance(eps, float):
                    pe_ratio = self._calc_pe(stock_price, eps)
                    
                    parsed_pe["data"].append({quarter:pe_ratio})

                else:
                    print(f"PE is N/A")

        # import json
        # print(json.dumps(parsed_pe, indent=2))

        format_logs(20, "ParsedPE", data["symbol"])
        return parsed_pe

if __name__ == "__main__":

    testObj = HyperAPI(load_api_key())

    # financials = testObj._req(resource="financials", symbol="aapl").json()
    # financials = testObj._parse_financials(symbol="amzn")

    # print(financials["financials"])
    # print(json.dumps(financials, indent=2))

    test_data = testObj._parse_financials("aapl")

    # testObj.eps_per_quarter(test_data)
    testObj.pe_per_quarter(test_data)
