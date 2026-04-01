"""
╔══════════════════════════════════════════════════════════╗
║   ANTIGRAVITY: ZERO-G INVENTORY — AI Advisor Module     ║
║   Intelligent Stock Analysis & Predictive Resupply       ║
╚══════════════════════════════════════════════════════════╝

This module analyses inventory data using rule-based AI logic to:
    • Predict stockout dates
    • Detect critically low items
    • Flag overstock situations
    • Generate actionable reorder recommendations
"""

from dataclasses import dataclass, field
from typing import Dict, List

from config import Config


# ── Data classes for structured analysis output ────────────

@dataclass
class StockAnalysis:
    """Analysis result for a single product."""
    product_code: str
    product_name: str
    current_stock: int
    daily_sales: float
    lead_time_days: int
    days_until_stockout: float
    status: str                     # "CRITICAL" | "WARNING" | "OVERSTOCK" | "HEALTHY"
    ai_message: str = ""
    recommended_order_qty: int = 0
    recommended_reorder_point: int = 0


@dataclass
class InventoryReport:
    """Aggregated analysis for the entire inventory."""
    total_products: int = 0
    critical_items: list = field(default_factory=list)
    warning_items: list = field(default_factory=list)
    overstock_items: list = field(default_factory=list)
    healthy_items: list = field(default_factory=list)
    analyses: list = field(default_factory=list)


class AIAdvisor:
    """
    AI-driven stock advisor that analyses inventory health.

    The advisor evaluates each product's trajectory based on:
        - days_until_stockout = current_stock / daily_sales
        - reorder_point       = daily_sales * lead_time * safety_factor
        - overstock detection  = stock > daily_sales * lead_time * overstock_multiplier

    Thresholds are configured in config.Config.
    """

    def __init__(self):
        self._critical_days = Config.CRITICAL_DAYS_THRESHOLD
        self._warning_days = Config.WARNING_DAYS_THRESHOLD
        self._overstock_mult = Config.OVERSTOCK_MULTIPLIER
        self._safety_mult = Config.SAFETY_STOCK_MULTIPLIER

    # ── Single-product analysis ────────────────────────────
    def analyze_product(self, product: dict) -> StockAnalysis:
        """
        Run AI analysis on a single product document.

        Args:
            product: Inventory document dict.

        Returns:
            StockAnalysis with status, message, and recommendation.
        """
        code = product.get("product_code", "N/A")
        name = product.get("product_name", "Unknown")
        stock = product.get("current_stock", 0)
        daily = product.get("daily_sales", 0)
        lead = product.get("lead_time_days", 0)

        # ── Calculate days until stockout ──────────────────
        if daily > 0:
            days_left = stock / daily
        else:
            days_left = float("inf")

        # ── Recommended reorder point ──────────────────────
        reorder_point = int(daily * lead * self._safety_mult)

        # ── Recommended order quantity (EOQ-simplified) ────
        # Order enough to cover lead_time + safety buffer
        recommended_qty = max(0, int(daily * lead * self._safety_mult) - stock)

        # ── Determine status ──────────────────────────────
        overstock_threshold = daily * lead * self._overstock_mult

        if daily <= 0 and stock > 0:
            status = "HEALTHY"
            ai_msg = self._msg_no_sales(name, stock)

        elif days_left <= self._critical_days:
            status = "CRITICAL"
            ai_msg = self._msg_critical(name, stock, days_left, lead, recommended_qty)

        elif days_left <= self._warning_days:
            status = "WARNING"
            ai_msg = self._msg_warning(name, stock, days_left, lead, recommended_qty)

        elif stock > overstock_threshold and overstock_threshold > 0:
            status = "OVERSTOCK"
            excess = int(stock - (daily * lead * self._safety_mult))
            ai_msg = self._msg_overstock(name, stock, days_left, excess)

        else:
            status = "HEALTHY"
            ai_msg = self._msg_healthy(name, stock, days_left)

        return StockAnalysis(
            product_code=code,
            product_name=name,
            current_stock=stock,
            daily_sales=daily,
            lead_time_days=lead,
            days_until_stockout=round(days_left, 1),
            status=status,
            ai_message=ai_msg,
            recommended_order_qty=recommended_qty,
            recommended_reorder_point=reorder_point,
        )

    # ── Full inventory scan ────────────────────────────────
    def scan_inventory(self, products: List[Dict]) -> InventoryReport:
        """
        Perform a full AI scan across all inventory items.

        Args:
            products: List of inventory document dicts.

        Returns:
            InventoryReport with categorized results.
        """
        report = InventoryReport(total_products=len(products))

        for product in products:
            analysis = self.analyze_product(product)
            report.analyses.append(analysis)

            if analysis.status == "CRITICAL":
                report.critical_items.append(analysis)
            elif analysis.status == "WARNING":
                report.warning_items.append(analysis)
            elif analysis.status == "OVERSTOCK":
                report.overstock_items.append(analysis)
            else:
                report.healthy_items.append(analysis)

        return report

    # ── AI Message Generators ──────────────────────────────
    @staticmethod
    def _msg_critical(name, stock, days_left, lead, order_qty):
        return (
            f"🔴 CRITICAL ALERT for '{name}':\n"
            f"   Current stock: {stock} units — estimated stockout in "
            f"{days_left:.1f} days.\n"
            f"   Lead time is {lead} days — resupply window has CLOSED.\n"
            f"   ➤ AI Recommendation: Place an EMERGENCY order of "
            f"{order_qty} units immediately.\n"
            f"   ➤ Consider express shipping to prevent service disruption."
        )

    @staticmethod
    def _msg_warning(name, stock, days_left, lead, order_qty):
        return (
            f"🟡 WARNING for '{name}':\n"
            f"   Current stock: {stock} units — estimated stockout in "
            f"{days_left:.1f} days.\n"
            f"   Lead time is {lead} days — order window is narrowing.\n"
            f"   ➤ AI Recommendation: Schedule a resupply of "
            f"{order_qty} units within the next 1-2 days."
        )

    @staticmethod
    def _msg_overstock(name, stock, days_left, excess):
        return (
            f"🟣 OVERSTOCK DETECTED for '{name}':\n"
            f"   Current stock: {stock} units — enough for "
            f"{days_left:.1f} days.\n"
            f"   Excess inventory: ~{excess} units above optimal level.\n"
            f"   ➤ AI Recommendation: Pause reordering. Consider promotions "
            f"or redistribution to reduce carrying costs."
        )

    @staticmethod
    def _msg_healthy(name, stock, days_left):
        return (
            f"🟢 '{name}' is in healthy orbit.\n"
            f"   Current stock: {stock} units — runway of "
            f"{days_left:.1f} days.\n"
            f"   ➤ No action needed. Stock trajectory is stable."
        )

    @staticmethod
    def _msg_no_sales(name, stock):
        return (
            f"🔵 '{name}' has no recorded daily sales.\n"
            f"   Current stock: {stock} units — unable to project runway.\n"
            f"   ➤ AI Recommendation: Verify sales data or mark as "
            f"slow-moving inventory."
        )

    # ── Report pretty-printer ──────────────────────────────
    @staticmethod
    def print_report(report: InventoryReport):
        """Display the full AI inventory report to the console."""
        div = Config.MESSAGES["divider"]

        print(f"\n{div}")
        print("  🤖 ANTIGRAVITY AI — INVENTORY HEALTH REPORT")
        print(f"{div}")
        print(f"  Total products scanned : {report.total_products}")
        print(f"  🔴 Critical            : {len(report.critical_items)}")
        print(f"  🟡 Warning             : {len(report.warning_items)}")
        print(f"  🟣 Overstock           : {len(report.overstock_items)}")
        print(f"  🟢 Healthy             : {len(report.healthy_items)}")
        print(div)

        # Show critical & warning first, then overstock
        priority_items = (
            report.critical_items
            + report.warning_items
            + report.overstock_items
        )

        if priority_items:
            print("\n  ── ACTION REQUIRED ─────────────────────────")
            for item in priority_items:
                print(f"\n{item.ai_message}")
        else:
            print("\n  ✅ All systems nominal — no action required.")

        print(f"\n{div}")
        print("  Lojistik yükü optimize edildi — Zero-G efficiency achieved.")
        print(f"{div}\n")
