import asyncio
import gc
from typing import Optional
import logging
from app.core.logger import get_logger

logger = get_logger(__name__)

# 1. Tuning 1: Reduce GC frequency (larger thresholds) -> prevent aggressive clean up
# GC will run Gen0 when 2,000 new allocations minus deallocations have happened.
# After Gen0 runs 20 times, promote objects and run Gen1.
# After Gen1 runs 20 times, run Gen2 (full GC, very expensive).
# Note: Gen0 is least expensive clean up and Gen2 is the most expensive clean up but it's more thorough
gc.set_threshold(2000, 20, 20)

# 2. Tuning 2: make the GC run every 15 sec in the background instead of constantly running -> prevent cleaning happening during request handling
# Why do we need GC Background worker?
# Reason: As Python Automatic GC runs at unpredictable times - often during API request -> we need GC Background worker to run GC outside request handling in the background to avoid any added latency during request time
async def gc_background_worker(interval_sec: int = 15):
    """
    Runs GC periodically to avoid stopping requests
    """
    while True:
        await asyncio.sleep(interval_sec)
        try:
            collected = gc.collect()
            logger.debug(f"[GC] collected={collected}")
        except Exception:
            logger.error("Unhandled exception in GC")
            pass

# 3. Tuning 3: Disable GC during requests -> prevent random pauses caused by GC
# Insight 1: Although Tuning 2 will help GC run outside of request handling, Python's normal GC still sometime runs during the request. Our Background GC worker doesn't stop the Python default GC from running -> That's why we need Tuning 3 to completely stop GC during the request.
# Insight 2: if we only have Tuning 3 without Tuning 2, during high request traffic, GC will never run. Garbage will pile up -> potential memory leak => Tuning 2 will make sure there's always a background GC worker running no matter what every 15 sec and outside the request handling
class RequestGCTuner: # This is a context manager
    """
    Context manager:
    - disables GC before request
    - re-enables after
    """
    def __enter__(self):
        self.was_enabled = gc.isenabled()
        gc.disable()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.was_enabled:
            gc.enable()