"""
Taxonomy Compatibility Validator for Myntra Sense Shortlist Comparison Service.
Prevents cross-category comparison mismatches (CP-01) and provides smart category grouping.
"""

from typing import Dict, Any, List, Tuple


class TaxonomyValidator:
    def validate_comparable_products(self, products: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validates whether selected products share compatible category taxonomy.
        """
        if len(products) < 2:
            return False, "Please select at least 2 products to compare."
            
        if len(products) > 4:
            return False, "You can compare up to 4 products at a time."
            
        categories = set(p.get("category_id", "UNKNOWN") for p in products)
        
        # Allow if all share the exact same category
        if len(categories) == 1:
            return True, "VALID"
            
        # Check compatible macro-categories
        compatible_groups = [
            {"MEN_CASUAL_SHIRTS", "MEN_FORMAL_SHIRTS", "MEN_CASUAL_TEES"},
            {"WOMEN_ETHNIC_KURTAS", "WOMEN_KURTA_SETS", "WOMEN_DRESSES"},
            {"FOOTWEAR_SPORTS", "FOOTWEAR_CASUAL_SNEAKERS"},
            {"MEN_TROUSERS", "MEN_JEANS", "MEN_CHINOS"},
        ]
        
        for group in compatible_groups:
            if categories.issubset(group):
                return True, "VALID_COMPATIBLE_MACRO_CATEGORY"
                
        return False, f"Incompatible product types ({', '.join(categories)}). Please select items from the same category (e.g. Shirts or Footwear) to compare."
