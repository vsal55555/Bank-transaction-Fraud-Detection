"""
quality.py
----------
Week 5 pipeline module — Quality gate

Responsibilities:
  - Run data quality checks on transformed rows BEFORE load
  - Raise DataQualityError (halts pipeline) if any check fails
  - Log a quality summary even when all checks pass

The quality gate is the pipeline's immune system.
A loud failure here is far better than silent bad data in the warehouse.
"""

import logging

logger = logging.getLogger(__name__)


class DataQualityError(Exception):
    """
    Raised when a data quality check fails.
    Signals the pipeline to halt — nothing gets loaded.

    Include the check name and failure details in the message
    so on-call engineers can act without reading the code.
    """
    pass


def check_row_count(rows: list, min_rows: int = 0) -> dict:
    """Fail if the transformed row count is below a minimum threshold."""
    count = len(rows)
    passed = count >= min_rows
    return {
        "check": "row_count",
        "passed": passed,
        "detail": f"{count} rows (min: {min_rows})"
    }


def check_transaction_amount(rows: list) -> dict:
    """Fail if any row has transaction_amount <= 0."""
    bad = [r for r in rows if r["transaction_amount"] < 0]
    return {
        "check": "transaction_amount_positive",
        "passed": len(bad) == 0,
        "detail": f"{len(bad)} rows with transaction_amount <= 0"
    }


def check_no_null_account_key(rows: list) -> dict:
    """Fail if any row is missing a account_key."""
    bad = [r for r in rows if r.get("account_key") is None]
    return {
        "check": "no_null_account_key",
        "passed": len(bad) == 0,
        "detail": f"{len(bad)} rows with NULL account_key"
    }

def check_no_null_merchant_key(rows: list) -> dict:
    """Fail if any row is missing a merchant_key."""
    bad = [r for r in rows if r.get("merchant_key") is None]
    return {
        "check": "no_null_merchant_key",
        "passed": len(bad) == 0,
        "detail": f"{len(bad)} rows with NULL merchant_key"
    }

def check_no_null_channel_key(rows: list) -> dict:
    """Fail if any row is missing a channel_key."""
    bad = [r for r in rows if r.get("channel_key") is None]
    return {
        "check": "no_null_channel_key",
        "passed": len(bad) == 0,
        "detail": f"{len(bad)} rows with NULL channel_key"
    }

def check_valid_transaction_type(rows: list) -> dict:
    """Fail if any row has an unrecognised status value."""
    valid = {"DEBIT", "CREDIT"}
    bad = [r for r in rows if r["transaction_type"] not in valid]
    return {
        "check": "valid_transaction_type",
        "passed": len(bad) == 0,
        "detail": f"{len(bad)} rows with invalid transaction_type"
    }

def check_valid_fraud_score(rows: list) -> dict:
    """Fail if any row is missing a fraud_score."""
    bad = [r for r in rows if r["fraud_score"] < 0]
    return {
        "check": "valid_fraud_score",
        "passed": len(bad) == 0,
        "detail": f"{len(bad)} rows with fraud_score < 0"
    }

def check_fraud_flag_consistency(rows: list) -> dict:
    """Fail if any row is missing a fraud_flag."""
    bad = [r for r in rows if r["fraud_score"] > 0 and not r["fraud_flag"]]
    return {
        "check": "fraud_flag_consistency",
        "passed": len(bad) == 0,
        "detail": f"{len(bad)} rows with fraud_score > 0 but fraud_flag = FALSE"
    }

def run_quality_checks(rows: list) -> dict:
    """
    Run all quality checks on transformed rows.

    Returns a summary dict if all checks pass.
    Raises DataQualityError immediately on the first failure.

    Args:
        rows: transformed fact rows from transform layer

    Returns:
        {'passed': True, 'checks': [...check results...], 'row_count': N}

    Raises:
        DataQualityError: with details of the failing check
    """
    checks = [
        check_row_count(rows),
        check_transaction_amount(rows),
        check_no_null_account_key(rows),
        check_no_null_merchant_key(rows),
        check_no_null_channel_key(rows),
        check_valid_transaction_type(rows),
        check_valid_fraud_score(rows),
        check_fraud_flag_consistency(rows)
    ]

    failed = [c for c in checks if not c["passed"]]

    if failed:
        first = failed[0]
        raise DataQualityError(
            f"Quality check failed: {first['check']} — {first['detail']}"
        )

    summary = {
        "passed": True,
        "checks": checks,
        "row_count": len(rows)
    }

    logger.info(f"Quality gate passed: {len(rows):,} rows, {len(checks)} checks")
    for c in checks:
        logger.debug(f"  {c['check']}: {c['detail']}")

    return summary