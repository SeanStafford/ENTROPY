"""Decision logic for specialist agent invocation."""

from typing import Tuple, Optional, List, Dict
from loguru import logger


class SpecialistInvoker:
    """Decides when to invoke expensive specialist agents (conservative strategy)."""

    TECHNICAL_JARGON = {
        'indicators': ['rsi', 'macd', 'moving average', 'sma', 'ema', 'golden cross', 'death cross', 'bollinger', 'momentum', 'oscillator'],
        'analysis': ['technical analysis', 'fundamental analysis', 'valuation', 'dcf', 'intrinsic value', 'discounted cash flow'],
        'metrics': ['momentum', 'volatility', 'beta', 'sharpe ratio', 'overbought', 'oversold', 'resistance', 'support'],
        'comparative': ['relative strength', 'peer comparison', 'sector analysis', 'correlation']
    }

    DISSATISFACTION_MARKERS = [
        'not enough', 'more detail', 'elaborate', 'tell me more', "that's not helpful",
        'why did', 'what caused', "doesn't explain", 'but why', 'how come', 'what about',
        'is that all', 'too vague', 'be more specific', 'give me details', 'not satisfied',
        'disappointing', 'insufficient'
    ]

    DEPTH_REQUESTS = [
        'detailed analysis', 'comprehensive report', 'deep dive', 'full breakdown',
        'complete analysis', 'thorough examination', 'in-depth look', 'extensive analysis'
    ]

    POWER_USER_THRESHOLD = 10

    def should_invoke_specialist(self, query: str, conversation_history: List[Dict],
                                user_profile: Dict) -> Tuple[bool, Optional[str], str]:
        """Determine if specialist should be invoked immediately."""
        query_lower = query.lower()

        if self._contains_technical_jargon(query_lower):
            logger.info("Invoking Market Data Specialist: technical jargon detected")
            return (True, 'market_data', 'technical_jargon')

        if self._is_depth_request(query_lower):
            if any(term in query_lower for term in ['news', 'article', 'sentiment', 'narrative']):
                logger.info("Invoking News Specialist: explicit depth request")
                return (True, 'news', 'depth_request')
            else:
                logger.info("Invoking Market Data Specialist: explicit depth request")
                return (True, 'market_data', 'depth_request')

        if len(conversation_history) >= 2:
            if self._is_dissatisfied(query_lower):
                specialist = self._determine_specialist_from_context(query, conversation_history[-1].get('content', ''))
                logger.info(f"Invoking {specialist} Specialist: user dissatisfaction detected")
                return (True, specialist, 'dissatisfaction')

        query_count = user_profile.get('query_count', 0)
        if query_count >= self.POWER_USER_THRESHOLD:
            if any(word in query_lower for word in ['analyze', 'compare', 'evaluate', 'assess']):
                logger.info("Invoking Market Data Specialist: power user analytical query")
                return (True, 'market_data', 'power_user_analytical')

        logger.debug("Generalist handling query: no specialist trigger")
        return (False, None, 'generalist_sufficient')

    def should_prefetch_specialist(self, query: str, generalist_response: str,
                                   conversation_history: List[Dict]) -> Tuple[bool, Optional[str], str]:
        """Determine if specialist should be pre-fetched (only when >80% confidence)."""
        query_lower = query.lower()

        if any(phrase in query_lower for phrase in ['what moved', 'why did', 'what caused']):
            if len(generalist_response.split()) < 30 and '$' in generalist_response:
                logger.info("Pre-fetching News Specialist: 'what moved' query with brief response")
                return (True, 'news', 'what_moved_pattern')

        if self._has_followup_pattern(conversation_history):
            logger.info("Pre-fetching Market Data Specialist: user follow-up pattern detected")
            return (True, 'market_data', 'followup_pattern')

        user_query_count = len([m for m in conversation_history if m.get('role') == 'user'])
        if user_query_count >= 8:
            if any(word in query_lower for word in ['news', 'latest', 'recent', 'update']):
                if len(generalist_response.split()) < 40:
                    logger.info("Pre-fetching News Specialist: power user news query with brief response")
                    return (True, 'news', 'power_user_news')

        logger.debug("No pre-fetch: insufficient confidence")
        return (False, None, 'low_confidence')

    def extract_specialist_task(self, query: str, conversation_history: List[Dict],
                               specialist_type: str) -> str:
        """Extract focused task description for specialist."""
        recent_context = self._get_recent_context(conversation_history, max_turns=3)
        tickers = self._extract_tickers(query, conversation_history)

        if specialist_type == 'market_data':
            requirements = self._extract_analysis_requirements(query)
            task = f"""Analyze: {query}

Ticker(s): {', '.join(tickers) if tickers else 'Determine from query'}

Recent context:
{recent_context}

Requirements:
{requirements}

Provide comprehensive technical and fundamental analysis using all available market data tools."""

        elif specialist_type == 'news':
            search_focus = self._extract_news_focus(query)
            task = f"""News analysis: {query}

Ticker(s): {', '.join(tickers) if tickers else 'Determine from query'}

Recent context:
{recent_context}

Search focus:
{search_focus}

Use hybrid retrieval to find relevant articles and synthesize a comprehensive narrative."""
        else:
            task = f"Analyze: {query}\n\nRecent context:\n{recent_context}"

        return task

    def _contains_technical_jargon(self, query: str) -> bool:
        for category, terms in self.TECHNICAL_JARGON.items():
            if any(term in query for term in terms):
                return True
        return False

    def _is_depth_request(self, query: str) -> bool:
        return any(phrase in query for phrase in self.DEPTH_REQUESTS)

    def _is_dissatisfied(self, query: str) -> bool:
        return any(marker in query for marker in self.DISSATISFACTION_MARKERS)

    def _determine_specialist_from_context(self, query: str, previous_response: str) -> str:
        query_lower = query.lower()
        if any(word in query_lower for word in ['news', 'why', 'article', 'story', 'narrative', 'sentiment']):
            return 'news'
        if any(word in query_lower for word in ['price', 'data', 'number', 'indicator', 'technical']):
            return 'market_data'
        return 'market_data'

    def _has_followup_pattern(self, conversation_history: List[Dict]) -> bool:
        if len(conversation_history) < 4:
            return False
        user_messages = [m['content'].lower() for m in conversation_history if m.get('role') == 'user'][-4:]
        if len(user_messages) < 2:
            return False
        followup_indicators = ['why', 'how', 'what about', 'tell me', 'more', '?']
        recent_followups = [any(indicator in msg for indicator in followup_indicators) for msg in user_messages[-2:]]
        return sum(recent_followups) >= 2

    def _get_recent_context(self, conversation_history: List[Dict], max_turns: int = 3) -> str:
        if not conversation_history:
            return "No prior context"
        recent = conversation_history[-(max_turns * 2):]
        context_lines = []
        for msg in recent:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:200]
            context_lines.append(f"{role.title()}: {content}")
        return '\n'.join(context_lines)

    def _extract_tickers(self, query: str, conversation_history: List[Dict]) -> List[str]:
        all_tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AMZN', 'JPM', 'V',
                      'BRK-B', 'XOM', 'CVX', 'JNJ', 'UNH', 'PG', 'KO', 'NKE', 'BA', 'GE', 'TSLA', 'F']
        found_tickers = []
        query_upper = query.upper()
        for ticker in all_tickers:
            if ticker in query_upper:
                found_tickers.append(ticker)
        if not found_tickers and conversation_history:
            recent_text = ' '.join([m.get('content', '') for m in conversation_history[-3:]]).upper()
            for ticker in all_tickers:
                if ticker in recent_text and ticker not in found_tickers:
                    found_tickers.append(ticker)
        return found_tickers

    def _extract_analysis_requirements(self, query: str) -> str:
        requirements = []
        query_lower = query.lower()
        if any(term in query_lower for term in ['price', 'trading at', 'current']):
            requirements.append("- Current price and price changes")
        if any(term in query_lower for term in ['technical', 'indicator', 'rsi', 'macd', 'moving average']):
            requirements.append("- Technical indicators (RSI, MACD, moving averages)")
        if any(term in query_lower for term in ['compare', 'vs', 'versus', 'compared to']):
            requirements.append("- Cross-stock comparison analysis")
        if any(term in query_lower for term in ['momentum', 'trend', 'direction']):
            requirements.append("- Momentum and trend analysis")
        if any(term in query_lower for term in ['fundamental', 'valuation', 'metrics']):
            requirements.append("- Fundamental metrics and valuation")
        if not requirements:
            requirements.append("- Comprehensive analysis based on query")
        return '\n'.join(requirements)

    def _extract_news_focus(self, query: str) -> str:
        focus_points = []
        query_lower = query.lower()
        if any(term in query_lower for term in ['recent', 'latest', 'today', 'this week']):
            focus_points.append("- Focus on most recent articles")
        if any(term in query_lower for term in ['sentiment', 'mood', 'perception']):
            focus_points.append("- Analyze market sentiment and tone")
        if any(term in query_lower for term in ['moved', 'cause', 'driven', 'impact']):
            focus_points.append("- Identify price-moving events and catalysts")
        if any(term in query_lower for term in ['earnings', 'results', 'report']):
            focus_points.append("- Focus on earnings and financial results")
        if not focus_points:
            focus_points.append("- Comprehensive news coverage and synthesis")
        return '\n'.join(focus_points)
