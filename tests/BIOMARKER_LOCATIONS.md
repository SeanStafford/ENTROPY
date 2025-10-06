# Boundary Logging Biomarkers

**Purpose:** Track inter-domain communication for debugging DDD architecture
**Pattern:** `[BOUNDARY: Source→Destination]` and `[DIAGNOSTIC]`
**Added:** 2025-10-06 for integration testing
**Removal:** Delete lines below if no longer needed

---

## Locations (11 total)

### `entropy/contexts/generation/tools.py` (6 markers)
- Line 24: `[BOUNDARY: Generation→MarketData]` - MarketDataTools.get_price() entry
- Line 27: `[BOUNDARY: MarketData→Generation]` - MarketDataTools.get_price() success
- Line 33: `[BOUNDARY: MarketData→Generation]` - MarketDataTools.get_price() failure
- Line 108: `[BOUNDARY: Generation→Retrieval]` - RetrievalTools.search_news() entry
- Line 139: `[BOUNDARY: Retrieval→Generation]` - RetrievalTools.search_news() success
- Line 142: `[BOUNDARY: Retrieval→Generation]` - RetrievalTools.search_news() failure

### `entropy/api/main.py` (5 markers)
- Line 158: `[DIAGNOSTIC]` - Diagnostic endpoint retrieval success
- Line 165: `[DIAGNOSTIC]` - Diagnostic endpoint retrieval failure
- Line 182: `[DIAGNOSTIC]` - Diagnostic endpoint market data success
- Line 195: `[DIAGNOSTIC]` - Diagnostic endpoint market data failure
- Line 207: `[DIAGNOSTIC]` - Diagnostic endpoint generation check

---

**Quick Removal:**
```bash
# Remove all boundary markers
sed -i '/\[BOUNDARY:/d' entropy/contexts/generation/tools.py
sed -i '/\[DIAGNOSTIC\]/d' entropy/api/main.py
```
