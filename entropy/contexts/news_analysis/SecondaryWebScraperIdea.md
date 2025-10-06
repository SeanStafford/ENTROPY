# Secondary Web Scraper Idea

## Problem
yfinance news summaries are only 100-200 characters. Sometimes they are even blank. That is not much to work with for sentiment analysis or retrieval.

Example:
> "Nvidia Stock Rises. Sales From This Key Supplier Signals Strong AI Demand."

## What we have currently
We have `entropy/utils/web_helpers.py` with retry logic and `markdownify` library. yfinance gives us the article links in `canonicalUrl`.

## The idea
When article.text is too short, fetch the full article from article.link:
- Use web_helpers to get HTML
- Convert to markdown with markdownify
- Extract main content (filter out ads/navigation)
- Replace the short summary with full text

Could add `enrich_article_from_url()` method to NewsProcessor and make it optional since it's slow.

## Why we're not doing it now
- Rate limits would be a problem - scraping 100 articles takes 5-10 minutes and might get us blocked.
- Many sites have paywalls (WSJ, Bloomberg) so we'd only get the teaser anyway.
- Legal gray area with ToS violations.
- Short summaries work fine for demonstrating core capabilities.

## If we want it later
Look at `trafilatura` library - it's really good at extracting main article content from messy HTML. Just add it as a dependency and write the method. Keep it optional and test on small batches first. Good for manual enrichment of important articles for demos, not for bulk processing.

## Notes
Infrastructure exists if we change our mind. Not worth the complexity right now.
