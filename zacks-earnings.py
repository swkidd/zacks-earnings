import pandas as pd
from dateutil import parser
import requests
import io
from typing import List, Optional
from datetime import datetime
import logging
from requests.exceptions import RequestException
from pandas.errors import EmptyDataError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ZacksError(Exception):
    """Base exception class for ZacksEarnings errors"""
    pass

class ZacksRequestError(ZacksError):
    """Raised when there's an error making requests to Zacks"""
    pass

class ZacksParsingError(ZacksError):
    """Raised when there's an error parsing data from Zacks"""
    pass

class ZacksEarnings:
    _ZACKS_URL = 'https://www.zacks.com/stock/quote/{}/detailed-estimates'
    _ZACKS_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    }
    
    @staticmethod
    def get_next_earnings_estimate(symbol: str) -> List[datetime]:
        """
        Get the next earnings estimate date for a given stock symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            
        Returns:
            List[datetime]: List containing the next earnings date if found, empty list otherwise
            
        Raises:
            ZacksRequestError: If there's an error making the request to Zacks
            ZacksParsingError: If there's an error parsing the response data
        """
        try:
            logger.info(f"Fetching next earnings estimate for {symbol}")
            r = requests.get(
                ZacksEarnings._ZACKS_URL.format(symbol.lower()),
                headers=ZacksEarnings._ZACKS_HEADER,
                timeout=10
            )
            r.raise_for_status()
            
            # Try multiple parsing approaches
            try:
                # First attempt: Look for tables containing earnings-related keywords
                all_tables = pd.read_html(r.content)
                for table in all_tables:
                    # Convert table to string to make text searching easier
                    table_str = str(table)
                    if any(keyword in table_str.lower() for keyword in ['next report', 'earnings date', 'next earnings']):
                        # Search through the table for date-like strings
                        for col in table.columns:
                            for val in table[col]:
                                try:
                                    if isinstance(val, str):
                                        date = parser.parse(val, fuzzy=True)
                                        if date > datetime.now():  # Only return future dates
                                            logger.info(f"Successfully retrieved earnings date for {symbol}: {date}")
                                            return [date]
                                except ValueError:
                                    continue
                
                # Second attempt: Try to find any date-like strings in the HTML
                import re
                from bs4 import BeautifulSoup
                
                soup = BeautifulSoup(r.content, 'html.parser')
                # Look for common date containers
                date_containers = soup.find_all(['span', 'div', 'td'], 
                    class_=re.compile(r'date|earnings|report', re.I))
                
                for container in date_containers:
                    try:
                        date = parser.parse(container.text, fuzzy=True)
                        if date > datetime.now():  # Only return future dates
                            logger.info(f"Successfully retrieved earnings date for {symbol}: {date}")
                            return [date]
                    except ValueError:
                        continue
                
                logger.warning(f"No valid earnings date found for {symbol}")
                return []
                
            except ValueError as e:
                logger.error(f"Failed to parse tables for {symbol}: {str(e)}")
                return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {symbol}: {str(e)}")
            raise ZacksRequestError(f"Failed to fetch data for {symbol}: {str(e)}")
            
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse earnings data for {symbol}: {str(e)}")
            raise ZacksParsingError(f"Failed to parse earnings data for {symbol}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error for {symbol}: {str(e)}")
            raise ZacksError(f"Unexpected error processing {symbol}: {str(e)}")

    @staticmethod
    def earnings_by_date(date: datetime) -> pd.DataFrame:
        """
        Get all earnings reports for a specific date.
        
        Args:
            date (datetime): The date to get earnings for
            
        Returns:
            pd.DataFrame: DataFrame containing earnings data
            
        Raises:
            ZacksRequestError: If there's an error making the request to Zacks
            ZacksParsingError: If there's an error parsing the response data
        """
        site = 'https://www.zacks.com/research/earnings/earning_export.php?timestamp={}&tab_id=1'
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            logger.info(f"Fetching earnings data for date: {date}")
            response = requests.get(
                site.format(int(date.timestamp())),
                headers=header,
                timeout=10
            )
            response.raise_for_status()
            
            df = pd.read_csv(
                io.StringIO(response.content.decode('utf-8')),
                sep='\t'
            )
            
            if df.empty:
                logger.warning(f"No earnings data found for date: {date}")
            else:
                logger.info(f"Successfully retrieved {len(df)} earnings entries for {date}")
                
            return df
            
        except RequestException as e:
            logger.error(f"Request failed for date {date}: {str(e)}")
            raise ZacksRequestError(f"Failed to fetch earnings data for {date}: {str(e)}")
            
        except EmptyDataError as e:
            logger.error(f"No data returned for date {date}: {str(e)}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Unexpected error for date {date}: {str(e)}")
            raise ZacksError(f"Unexpected error processing earnings for {date}: {str(e)}")

def main():
    try:
        # Test earnings by date
        test_date = parser.parse('Aug 12, 2024')
        earnings = ZacksEarnings.earnings_by_date(test_date)
        print(f'\nEarnings for {test_date.strftime("%B %d, %Y")}:')
        print(earnings)

        # Test next earnings estimate
        symbol = 'AAPL'
        next_earnings_date = ZacksEarnings.get_next_earnings_estimate(symbol)
        if next_earnings_date:
            print(f'\n{symbol} Estimated Earnings Date: {next_earnings_date[0].strftime("%Y-%m-%d")}')
        
    except ZacksError as e:
        logger.error(f"Application error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")

if __name__ == "__main__":
    main()
