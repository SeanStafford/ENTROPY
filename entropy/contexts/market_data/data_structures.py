from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StockPrice(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volume: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class StockFundamentals(BaseModel):
    ticker: str
    market_cap: Optional[int] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    fifty_day_avg: Optional[float] = None
    two_hundred_day_avg: Optional[float] = None
    # 52-week range helps identify volatility bounds
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    company_name: Optional[str] = None


class PricePoint(BaseModel):
    date: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None


class PriceHistory(BaseModel):
    ticker: str
    prices: List[PricePoint]
    period: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class PriceChange(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    previous_price: Optional[float] = None
    change_amount: Optional[float] = None
    change_percent: Optional[float] = None
    period: str


class TechnicalIndicator(BaseModel):
    ticker: str
    indicator_type: str
    value: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    # stores params like window size, etc
    parameters: Dict[str, Any] = Field(default_factory=dict)


class PerformanceResult(BaseModel):
    ticker: str
    value: Optional[float] = None
    metric: str


class PerformanceComparison(BaseModel):
    tickers: List[str]
    metric: str
    # sorted by value descending
    results: List[PerformanceResult]
    period: str
