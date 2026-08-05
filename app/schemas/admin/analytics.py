"""Admin analytics schemas."""

from __future__ import annotations

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    period: str
    total_views: int
    unique_sessions: int


class PageBreakdown(BaseModel):
    path: str
    views: int


class ReferrerBreakdown(BaseModel):
    referrer: str
    views: int


class CountryBreakdown(BaseModel):
    country: str
    views: int


class DailyViews(BaseModel):
    date: str
    views: int


class AnalyticsSummaryOut(BaseModel):
    period: str
    total_views: int
    unique_sessions: int
    top_page: str | None
    daily: list[DailyViews]


class AnalyticsPagesOut(BaseModel):
    period: str
    pages: list[PageBreakdown]


class AnalyticsReferrersOut(BaseModel):
    period: str
    referrers: list[ReferrerBreakdown]


class AnalyticsCountriesOut(BaseModel):
    period: str
    countries: list[CountryBreakdown]
