#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Adapt Harbor's async evaluator to GEPA 0.1.2's synchronous callback API."""
import asyncio
import threading


class AsyncEvaluatorBridge:
    """Keep every concurrent development trial on one stable event loop."""

    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, name="svg-harbor-evaluations", daemon=True)
        self.thread.start()

    def __call__(self, candidate, example):
        return asyncio.run_coroutine_threadsafe(self.evaluator(candidate, example), self.loop).result()

    def close(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=10)
        if self.thread.is_alive():
            raise RuntimeError("The evaluation event loop did not stop")
        self.loop.close()
