"""
╔══════════════════════════════════════════════════════════╗
║   ANTIGRAVITY: ZERO-G INVENTORY — Inventory Module      ║
║   Cargo Bay Management & Orbital Stock Control           ║
╚══════════════════════════════════════════════════════════╝
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pymongo.errors import DuplicateKeyError
from config import Config


class InventoryManager:
    """
    CRUD operations for the inventory collection.

    Each inventory document follows this schema:
    {
        "product_code"  : str,   # Unique product identifier
        "product_name"  : str,   # Human-readable name
        "category"      : str,   # Product category
        "current_stock" : int,   # Mevcut Stok
        "daily_sales"   : float, # Günlük Satış (avg units/day)
        "lead_time_days": int,   # Tedarik Süresi (days)
        "unit_price"    : float, # Price per unit
        "added_by"      : str,   # Username who added the item
        "updated_at"    : datetime
    }
    """

    def __init__(self, inventory_collection):
        self._inventory = inventory_collection

    # ── CREATE ─────────────────────────────────────────────
    def add_product(self, product_data: dict, added_by: str) -> bool:
        """
        Add a new product to the inventory orbit.

        Args:
            product_data: Dict with product_code, product_name, category,
                          current_stock, daily_sales, lead_time_days, unit_price.
            added_by    : Username of the operator.

        Returns:
            True on success, False on duplicate or error.
        """
        try:
            product_data["added_by"] = added_by
            product_data["updated_at"] = datetime.now(timezone.utc)
            self._inventory.insert_one(product_data)
            print(Config.MESSAGES["add_success"])
            return True

        except DuplicateKeyError:
            print(f"  ⚠️  Product code '{product_data.get('product_code')}' "
                  "already exists in orbit.")
            return False

        except Exception as exc:
            print(Config.MESSAGES["error"].format(error=exc))
            return False

    # ── READ ───────────────────────────────────────────────
    def get_all_products(self) -> List[Dict]:
        """Retrieve all products from the cargo bay."""
        try:
            return list(self._inventory.find({}, {"_id": 0}))
        except Exception as exc:
            print(Config.MESSAGES["error"].format(error=exc))
            return []

    def get_product(self, product_code: str) -> Optional[Dict]:
        """Retrieve a single product by its code."""
        try:
            return self._inventory.find_one(
                {"product_code": product_code}, {"_id": 0}
            )
        except Exception as exc:
            print(Config.MESSAGES["error"].format(error=exc))
            return None

    def search_products(self, keyword: str) -> List[Dict]:
        """Search products by name (case-insensitive partial match)."""
        try:
            regex_filter = {"product_name": {"$regex": keyword, "$options": "i"}}
            return list(self._inventory.find(regex_filter, {"_id": 0}))
        except Exception as exc:
            print(Config.MESSAGES["error"].format(error=exc))
            return []

    # ── UPDATE ─────────────────────────────────────────────
    def update_product(self, product_code: str, updates: dict) -> bool:
        """
        Update fields of an existing product.

        Args:
            product_code: The product to update.
            updates     : Dict of fields to change.

        Returns:
            True if a document was modified, False otherwise.
        """
        try:
            updates["updated_at"] = datetime.now(timezone.utc)
            result = self._inventory.update_one(
                {"product_code": product_code},
                {"$set": updates},
            )
            if result.modified_count > 0:
                print(Config.MESSAGES["update_success"])
                return True
            print(f"  ⚠️  No product found with code '{product_code}'.")
            return False

        except Exception as exc:
            print(Config.MESSAGES["error"].format(error=exc))
            return False

    # ── DELETE ─────────────────────────────────────────────
    def remove_product(self, product_code: str) -> bool:
        """Remove a product from the inventory orbit."""
        try:
            result = self._inventory.delete_one({"product_code": product_code})
            if result.deleted_count > 0:
                print(Config.MESSAGES["remove_success"])
                return True
            print(f"  ⚠️  No product found with code '{product_code}'.")
            return False

        except Exception as exc:
            print(Config.MESSAGES["error"].format(error=exc))
            return False

    # ── HELPERS ────────────────────────────────────────────
    def count(self) -> int:
        """Return the total number of products in orbit."""
        try:
            return self._inventory.count_documents({})
        except Exception as exc:
            print(Config.MESSAGES["error"].format(error=exc))
            return 0
