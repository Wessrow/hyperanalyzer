#!/usr/bin/python3

"""
The purpose of this code is to scrape the Hypercharts API
Code written by Gustav Larsson
"""

import os
import json
import requests

def load_api_key():
    """
    Helper function to load API-key.
    """

    api_key = os.environ.get("API_KEY")

    return api_key

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
        # params = f"?symbol={symbol}&apiKey=poop"
        
        response = requests.get(f"{self.base_url}/{resource}{params}")

        if response.status_code == 200:
            return response

        elif response.status_code == 404:

            message = {"error": response.status_code,
                        "message": f"Resource '{resource}' does not exist"
            }
            
            return message

        elif response.status_code == 400:
            
            error_message = response.json()["error"]
            
            message = {"error": response.status_code,
                        "message": error_message
            }
            
            return message

    def _parse_financials(self, category, symbol="aapl"):
        """
        Private helper function to parse relevant financial info
        """

        relevant_info = {}

        raw_info = self._req(resource="financials", symbol=symbol).json()

        for quarter in raw_info["financials"]:
            print(f"{quarter['Net Income']}")

if __name__ == "__main__":

    testObj = HyperAPI(load_api_key())

    #financials = testObj._req(resource="financials", symbol="aapl").json()

    #print(json.dumps(financials, indent=2))
    #print(financials["financials"])

    # print(testObj._req(resource="financials", symbol="poop"))



    
