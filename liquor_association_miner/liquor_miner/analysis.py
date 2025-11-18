import pandas as pd
from apyori import apriori
import os
from typing import List, Dict, Any, Tuple

# Caching variables
_CACHED_RULES = None
_CACHED_ITEMS = None

# Robust file path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, '..', 'data', 'liquor_transactions_separated.csv')


def _load_and_process_data() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Internal function to run Apriori and populate the cache."""
    global _CACHED_RULES, _CACHED_ITEMS

    if _CACHED_RULES is not None and _CACHED_ITEMS is not None:
        return _CACHED_RULES, _CACHED_ITEMS

    try:
        df = pd.read_csv(DATA_FILE)
        records = df.drop('TransactionID', axis=1).apply(lambda x: x.dropna().tolist(), axis=1).tolist()

        all_items = set()
        for transaction in records:
            all_items.update(transaction)
        _CACHED_ITEMS = sorted(list(all_items))

    except FileNotFoundError as e:
        error_msg = f"Dataset file not found at: {e.filename}. Ensure data/liquor_transactions_separated.csv exists."
        return [{"error": error_msg}], []
    except Exception as e:
        error_msg = f"An error occurred during data processing: {e}"
        return [{"error": error_msg}], []

        # Temporarily lower support to find rare multi-item rules
    NEW_MIN_SUPPORT = 0.001
    NEW_MIN_CONFIDENCE = 0.05  # Loosen confidence too
    NEW_MIN_LIFT = 1.0
    association_rules = apriori(
        records,
        min_support=NEW_MIN_SUPPORT,
        min_confidence=NEW_MIN_CONFIDENCE,
        min_lift=NEW_MIN_LIFT,
        min_length=2
    )

    results = []
    for rule in association_rules:
        if not rule.ordered_statistics: continue

        statistic = rule.ordered_statistics[0]

        # FIX 1: Convert frozenset to list for antecedent
        antecedent_items = list(statistic.items_base)

        # FIX 2: Convert frozenset to list and safely extract the first item for the consequent
        consequent_items_list = list(statistic.items_add)
        consequent = consequent_items_list[0] if consequent_items_list else ""

        if not antecedent_items or not consequent: continue

        results.append({
            "antecedent": antecedent_items,
            "consequent": consequent,
            "rule": f"({', '.join(antecedent_items)}) → ({consequent})",
            "support": round(rule.support, 4),
            "confidence": round(statistic.confidence, 4),
            "lift": round(statistic.lift, 4)
        })

    _CACHED_RULES = results
    return _CACHED_RULES, _CACHED_ITEMS


def get_association_rules():
    rules, _ = _load_and_process_data()
    return rules


def get_unique_items():
    _, items = _load_and_process_data()
    return items


def get_recommendations(selected_item: str) -> List[Dict[str, Any]]:
    """
    Finds INVERSE recommendations: Rules where selected_item is the CONSEQuent (B)
    and the recommendation is the ANTECEdent (A). (A -> B)
    """
    rules, _ = _load_and_process_data()
    recommendations = []

    if rules and isinstance(rules, list) and "error" in rules[0]:
        return rules

        # Find rules where the selected item is the CONSEQuent
    for rule in rules:
        if rule['consequent'] == selected_item:
            recommendations.append(rule)

    # Sort results by Lift (descending)
    recommendations.sort(key=lambda x: x['lift'], reverse=True)

    return recommendations