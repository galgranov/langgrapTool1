"""
Tools for the Company Research Agent.
Each tool is a standalone function that can be used by the agent.
"""
import requests
import time
from typing import Dict, Any
from langchain_core.tools import tool
from datadog_tracing import trace_tool
from datadog_metrics import track_api_call
from datadog_logger import get_logger, log_api_call

# Initialize logger
logger = get_logger(__name__, agent_name="company_tools")


@tool
@trace_tool("get_company_info", api_name="yahoo_finance")
def get_company_info_tool(ticker: str) -> Dict[str, Any]:
    """Fetch company information using Yahoo Finance API.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
        
    Returns:
        Dictionary with company information or error
    """
    if not ticker:
        return {"success": False, "error": "No ticker provided", "data": None}
    
    start_time = time.time()
    ticker = ticker.upper()
    
    try:
        logger.info(f"Fetching company info for {ticker}")
        
        # Using Yahoo Finance alternative API
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {
            "modules": "assetProfile,summaryDetail,price"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('quoteSummary', {}).get('result', [])
            
            if not result:
                return {
                    "success": False,
                    "error": f"No data found for ticker {ticker}",
                    "data": None
                }
            
            info = result[0]
            profile = info.get('assetProfile', {})
            price_data = info.get('price', {})
            summary = info.get('summaryDetail', {})
            
            return {
                "success": True,
                "data": {
                    "ticker": ticker,
                    "name": price_data.get('longName', 'N/A'),
                    "industry": profile.get('industry', 'N/A'),
                    "sector": profile.get('sector', 'N/A'),
                    "website": profile.get('website', 'N/A'),
                    "description": profile.get('longBusinessSummary', 'N/A'),
                    "employees": profile.get('fullTimeEmployees', 'N/A'),
                    "city": profile.get('city', 'N/A'),
                    "state": profile.get('state', 'N/A'),
                    "country": profile.get('country', 'N/A'),
                    "market_cap": summary.get('marketCap', {}).get('fmt', 'N/A'),
                }
            }
        else:
            return {
                "success": False,
                "error": f"Could not fetch data for {ticker}. Status: {response.status_code}",
                "data": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching company info: {str(e)}",
            "data": None
        }


@tool
def get_stock_price_tool(ticker: str) -> Dict[str, Any]:
    """Fetch current stock price and trading data.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with stock price data or error
    """
    if not ticker:
        return {"success": False, "error": "No ticker provided", "data": None}
    
    try:
        ticker = ticker.upper()
        
        # Using Yahoo Finance API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {"interval": "1d", "range": "1d"}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('chart', {}).get('result', [])
            
            if not result:
                return {
                    "success": False,
                    "error": f"No price data found for {ticker}",
                    "data": None
                }
            
            quote = result[0]
            meta = quote.get('meta', {})
            indicators = quote.get('indicators', {}).get('quote', [{}])[0]
            
            current_price = meta.get('regularMarketPrice', 'N/A')
            prev_close = meta.get('previousClose', 'N/A')
            
            # Calculate change
            if current_price != 'N/A' and prev_close != 'N/A':
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
            else:
                change = 'N/A'
                change_percent = 'N/A'
            
            return {
                "success": True,
                "data": {
                    "ticker": ticker,
                    "current_price": current_price,
                    "currency": meta.get('currency', 'USD'),
                    "previous_close": prev_close,
                    "change": change,
                    "change_percent": change_percent,
                    "day_high": meta.get('regularMarketDayHigh', 'N/A'),
                    "day_low": meta.get('regularMarketDayLow', 'N/A'),
                    "volume": meta.get('regularMarketVolume', 'N/A'),
                    "market_state": meta.get('marketState', 'N/A'),
                }
            }
        else:
            return {
                "success": False,
                "error": f"Could not fetch price for {ticker}",
                "data": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching stock price: {str(e)}",
            "data": None
        }


@tool
def get_financial_metrics_tool(ticker: str) -> Dict[str, Any]:
    """Fetch key financial metrics and ratios.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with financial metrics or error
    """
    if not ticker:
        return {"success": False, "error": "No ticker provided", "data": None}
    
    try:
        ticker = ticker.upper()
        
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {
            "modules": "defaultKeyStatistics,financialData"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('quoteSummary', {}).get('result', [])
            
            if not result:
                return {
                    "success": False,
                    "error": f"No metrics found for {ticker}",
                    "data": None
                }
            
            info = result[0]
            stats = info.get('defaultKeyStatistics', {})
            financials = info.get('financialData', {})
            
            return {
                "success": True,
                "data": {
                    "ticker": ticker,
                    "pe_ratio": stats.get('trailingPE', {}).get('fmt', 'N/A'),
                    "forward_pe": stats.get('forwardPE', {}).get('fmt', 'N/A'),
                    "peg_ratio": stats.get('pegRatio', {}).get('fmt', 'N/A'),
                    "price_to_book": stats.get('priceToBook', {}).get('fmt', 'N/A'),
                    "dividend_yield": stats.get('dividendYield', {}).get('fmt', 'N/A'),
                    "profit_margin": financials.get('profitMargins', {}).get('fmt', 'N/A'),
                    "revenue_growth": financials.get('revenueGrowth', {}).get('fmt', 'N/A'),
                    "roe": financials.get('returnOnEquity', {}).get('fmt', 'N/A'),
                    "debt_to_equity": financials.get('debtToEquity', {}).get('fmt', 'N/A'),
                    "52week_high": stats.get('fiftyTwoWeekHigh', {}).get('fmt', 'N/A'),
                    "52week_low": stats.get('fiftyTwoWeekLow', {}).get('fmt', 'N/A'),
                }
            }
        else:
            return {
                "success": False,
                "error": f"Could not fetch metrics for {ticker}",
                "data": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching financial metrics: {str(e)}",
            "data": None
        }


@tool
def get_company_news_tool(ticker: str) -> Dict[str, Any]:
    """Fetch recent news about the company.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with news articles or error
    """
    if not ticker:
        return {"success": False, "error": "No ticker provided", "data": None}
    
    try:
        ticker = ticker.upper()
        
        # Note: This would require a news API key in production
        # For now, returning a placeholder
        return {
            "success": True,
            "data": {
                "ticker": ticker,
                "note": "News API integration would require an API key (NewsAPI, Finnhub, etc.)",
                "search_link": f"https://www.google.com/search?q={ticker}+stock+news&tbm=nws"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching company news: {str(e)}",
            "data": None
        }


@tool
def get_company_executives_tool(ticker: str) -> Dict[str, Any]:
    """Fetch company executives and key personnel.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with executives information or error
    """
    if not ticker:
        return {"success": False, "error": "No ticker provided", "data": None}
    
    try:
        ticker = ticker.upper()
        
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {
            "modules": "assetProfile"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('quoteSummary', {}).get('result', [])
            
            if not result:
                return {
                    "success": False,
                    "error": f"No data found for ticker {ticker}",
                    "data": None
                }
            
            profile = result[0].get('assetProfile', {})
            officers = profile.get('companyOfficers', [])
            
            if not officers:
                return {
                    "success": False,
                    "error": f"No executive information found for {ticker}",
                    "data": None
                }
            
            # Get top 10 executives
            executives = []
            for officer in officers[:10]:
                exec_info = {
                    "name": officer.get('name', 'N/A'),
                    "title": officer.get('title', 'N/A'),
                    "age": officer.get('age', 'N/A'),
                    "year_born": officer.get('yearBorn', 'N/A'),
                    "total_pay": officer.get('totalPay', {}).get('fmt', 'N/A') if officer.get('totalPay') else 'N/A',
                }
                executives.append(exec_info)
            
            return {
                "success": True,
                "data": {
                    "ticker": ticker,
                    "company_name": profile.get('longBusinessSummary', 'N/A')[:100] if profile.get('longBusinessSummary') else 'N/A',
                    "executives": executives,
                    "count": len(executives)
                }
            }
        else:
            return {
                "success": False,
                "error": f"Could not fetch executives for {ticker}. Status: {response.status_code}",
                "data": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching company executives: {str(e)}",
            "data": None
        }


# Tool registry for easy access
COMPANY_TOOLS = {
    "company_info": get_company_info_tool,
    "stock_price": get_stock_price_tool,
    "financial_metrics": get_financial_metrics_tool,
    "company_news": get_company_news_tool,
    "company_executives": get_company_executives_tool
}


def get_company_tool(tool_name: str):
    """Get a tool by name."""
    return COMPANY_TOOLS.get(tool_name)
