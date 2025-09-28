#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM usage monitoring and switching capability
"""
import time
import json
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class LLMUsageRecord:
    """Record of LLM API usage"""
    provider: str
    model: str
    timestamp: str
    tokens_used: int
    cost_estimate: float
    success: bool
    response_time: float


class LLMUsageMonitor:
    """Monitor LLM usage and implement switching logic"""

    def __init__(self, usage_log_path: str = "llm_usage.json"):
        self.usage_log_path = usage_log_path
        self.usage_records: List[LLMUsageRecord] = []
        self.load_usage_history()

        # Usage limits and costs (per 1000 tokens)
        self.provider_config = {
            'claude': {
                'models': ['claude-3.5-sonnet', 'claude-3-haiku'],
                'daily_limit': 1000000,  # tokens per day
                'cost_per_1k_tokens': 0.003,
                'priority': 1
            },
            'gemini': {
                'models': ['gemini-pro', 'gemini-pro-vision'],
                'daily_limit': 2000000,  # tokens per day
                'cost_per_1k_tokens': 0.0005,
                'priority': 2
            },
            'openai': {
                'models': ['gpt-4', 'gpt-3.5-turbo'],
                'daily_limit': 500000,  # tokens per day
                'cost_per_1k_tokens': 0.03,
                'priority': 3
            }
        }

        self.current_provider = 'claude'  # Default to Claude

    def load_usage_history(self):
        """Load usage history from JSON file"""
        try:
            with open(self.usage_log_path, 'r') as f:
                data = json.load(f)
                self.usage_records = [
                    LLMUsageRecord(**record) for record in data
                ]
        except FileNotFoundError:
            self.usage_records = []
        except Exception as e:
            print(f"Warning: Could not load usage history: {e}")
            self.usage_records = []

    def save_usage_history(self):
        """Save usage history to JSON file"""
        try:
            with open(self.usage_log_path, 'w') as f:
                json.dump([asdict(record) for record in self.usage_records], f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save usage history: {e}")

    def log_usage(self, provider: str, model: str, tokens_used: int,
                  success: bool, response_time: float) -> None:
        """Log LLM usage"""
        cost_estimate = tokens_used * self.provider_config[provider]['cost_per_1k_tokens'] / 1000

        record = LLMUsageRecord(
            provider=provider,
            model=model,
            timestamp=datetime.now().isoformat(),
            tokens_used=tokens_used,
            cost_estimate=cost_estimate,
            success=success,
            response_time=response_time
        )

        self.usage_records.append(record)
        self.save_usage_history()

    def get_daily_usage(self, provider: str, date: Optional[datetime] = None) -> Dict:
        """Get usage statistics for a provider on a specific date"""
        if date is None:
            date = datetime.now()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        daily_records = [
            record for record in self.usage_records
            if record.provider == provider and
            start_of_day <= datetime.fromisoformat(record.timestamp) < end_of_day
        ]

        total_tokens = sum(record.tokens_used for record in daily_records)
        total_cost = sum(record.cost_estimate for record in daily_records)
        success_count = sum(1 for record in daily_records if record.success)
        total_requests = len(daily_records)

        return {
            'provider': provider,
            'date': date.strftime('%Y-%m-%d'),
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'total_requests': total_requests,
            'success_rate': (success_count / total_requests * 100) if total_requests > 0 else 0,
            'limit_usage_percent': (total_tokens / self.provider_config[provider]['daily_limit'] * 100),
            'limit_exceeded': total_tokens > self.provider_config[provider]['daily_limit']
        }

    def check_and_switch_provider(self) -> str:
        """Check usage limits and switch provider if needed"""
        current_usage = self.get_daily_usage(self.current_provider)

        # Check if current provider has exceeded limits
        if current_usage['limit_exceeded'] or current_usage['limit_usage_percent'] > 90:
            print(f"[WARNING] {self.current_provider} usage limit approached/exceeded ({current_usage['limit_usage_percent']:.1f}%)")

            # Find alternative provider
            for provider in sorted(self.provider_config.keys(),
                                 key=lambda p: self.provider_config[p]['priority']):
                if provider != self.current_provider:
                    alt_usage = self.get_daily_usage(provider)
                    if not alt_usage['limit_exceeded'] and alt_usage['limit_usage_percent'] < 80:
                        print(f"[SWITCHING] Switching to {provider} (usage: {alt_usage['limit_usage_percent']:.1f}%)")
                        self.current_provider = provider
                        return provider

            print(f"[WARNING] All providers near limits, continuing with {self.current_provider}")

        return self.current_provider

    def get_recommended_model(self, provider: str) -> str:
        """Get recommended model for a provider"""
        models = self.provider_config[provider]['models']
        return models[0]  # Return primary model

    def get_usage_summary(self) -> Dict:
        """Get comprehensive usage summary"""
        summary = {}

        for provider in self.provider_config.keys():
            usage = self.get_daily_usage(provider)
            summary[provider] = usage

        # Add overall statistics
        total_cost_today = sum(data['total_cost'] for data in summary.values())
        total_requests_today = sum(data['total_requests'] for data in summary.values())

        summary['overall'] = {
            'total_daily_cost': total_cost_today,
            'total_daily_requests': total_requests_today,
            'current_provider': self.current_provider,
            'recommended_provider': self.check_and_switch_provider()
        }

        return summary

    def reset_daily_usage(self):
        """Reset usage tracking (for testing purposes)"""
        # Remove today's records
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.usage_records = [
            record for record in self.usage_records
            if datetime.fromisoformat(record.timestamp) < today
        ]
        self.save_usage_history()


# Example usage integration
class LLMApiClient:
    """Wrapper for LLM API calls with usage monitoring"""

    def __init__(self, monitor: LLMUsageMonitor):
        self.monitor = monitor

    def call_llm(self, prompt: str, context: str = "") -> Dict:
        """
        Make LLM API call with usage monitoring

        Args:
            prompt: The prompt to send
            context: Additional context

        Returns:
            Dict with response and metadata
        """
        # Get current provider and model
        provider = self.monitor.check_and_switch_provider()
        model = self.monitor.get_recommended_model(provider)

        start_time = time.time()

        try:
            # Here you would make the actual API call
            # For now, simulate the call
            estimated_tokens = len(prompt.split()) * 1.3  # Rough estimate

            # Simulate API response
            response = {
                'content': f"Simulated response from {provider}:{model}",
                'provider': provider,
                'model': model,
                'tokens_used': int(estimated_tokens),
                'success': True
            }

            response_time = time.time() - start_time

            # Log usage
            self.monitor.log_usage(
                provider=provider,
                model=model,
                tokens_used=response['tokens_used'],
                success=True,
                response_time=response_time
            )

            return response

        except Exception as e:
            response_time = time.time() - start_time

            # Log failed usage
            self.monitor.log_usage(
                provider=provider,
                model=model,
                tokens_used=0,
                success=False,
                response_time=response_time
            )

            raise e


def test_llm_monitor():
    """Test the LLM monitoring system"""
    monitor = LLMUsageMonitor()
    client = LLMApiClient(monitor)

    # Simulate some API calls
    for i in range(5):
        try:
            response = client.call_llm(f"Test prompt {i}")
            print(f"Call {i}: {response['provider']} used {response['tokens_used']} tokens")
        except Exception as e:
            print(f"Call {i} failed: {e}")

    # Print usage summary
    summary = monitor.get_usage_summary()
    print("\nUsage Summary:")
    for provider, data in summary.items():
        if provider != 'overall':
            print(f"{provider}: {data['total_tokens']} tokens, ${data['total_cost']:.4f}, {data['limit_usage_percent']:.1f}% of limit")


if __name__ == "__main__":
    test_llm_monitor()