"""
A-SOC Utility Functions
========================
Helper functions for the Aadhaar Security Operations Center system.
All functions are deterministic with fixed random seed = 42.
"""

import numpy as np
import pandas as pd
from typing import Union, Optional
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Fixed random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


def safe_divide(numerator: Union[float, pd.Series], 
                denominator: Union[float, pd.Series], 
                default: float = 0.0) -> Union[float, pd.Series]:
    """
    Safely divide two numbers or series, returning default on division by zero.
    
    Args:
        numerator: The numerator value(s)
        denominator: The denominator value(s)
        default: Value to return when denominator is zero
        
    Returns:
        Result of division or default value
    """
    if isinstance(numerator, pd.Series) and isinstance(denominator, pd.Series):
        result = numerator / denominator
        result = result.replace([np.inf, -np.inf], default)
        result = result.fillna(default)
        return result
    elif isinstance(numerator, pd.Series):
        if denominator == 0:
            return pd.Series([default] * len(numerator), index=numerator.index)
        return numerator / denominator
    elif isinstance(denominator, pd.Series):
        result = numerator / denominator
        result = result.replace([np.inf, -np.inf], default)
        result = result.fillna(default)
        return result
    else:
        if denominator == 0:
            return default
        return numerator / denominator


def clip_zscore(zscore: Union[float, pd.Series], 
                limit: float = 5.0) -> Union[float, pd.Series]:
    """
    Clip Z-scores to a specified range [-limit, +limit].
    
    Args:
        zscore: Z-score value(s) to clip
        limit: Maximum absolute value (default: 5.0)
        
    Returns:
        Clipped Z-score(s)
    """
    if isinstance(zscore, pd.Series):
        return zscore.clip(-limit, limit)
    return max(-limit, min(limit, zscore))


def normalize_to_scale(value: Union[float, pd.Series], 
                       min_val: float, 
                       max_val: float, 
                       target_min: float = 0.0, 
                       target_max: float = 10.0) -> Union[float, pd.Series]:
    """
    Normalize a value from [min_val, max_val] to [target_min, target_max].
    
    Args:
        value: Value(s) to normalize
        min_val: Original minimum value
        max_val: Original maximum value
        target_min: Target minimum (default: 0)
        target_max: Target maximum (default: 10)
        
    Returns:
        Normalized value(s)
    """
    if max_val == min_val:
        return target_min
    
    normalized = (value - min_val) / (max_val - min_val)
    scaled = normalized * (target_max - target_min) + target_min
    
    if isinstance(scaled, pd.Series):
        return scaled.clip(target_min, target_max)
    return max(target_min, min(target_max, scaled))


def get_risk_category(score: Union[float, pd.Series]) -> Union[str, pd.Series]:
    """
    Convert numeric risk score to categorical risk level.
    
    Risk Categories:
    - Critical: >= 8
    - High: 6 - 7.99
    - Medium: 4 - 5.99
    - Low: < 4
    
    Args:
        score: Risk score value(s)
        
    Returns:
        Risk category string(s)
    """
    if isinstance(score, pd.Series):
        conditions = [
            score >= 8,
            (score >= 6) & (score < 8),
            (score >= 4) & (score < 6),
            score < 4
        ]
        choices = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        return pd.Series(np.select(conditions, choices, default='LOW'), index=score.index)
    else:
        if score >= 8:
            return 'CRITICAL'
        elif score >= 6:
            return 'HIGH'
        elif score >= 4:
            return 'MEDIUM'
        else:
            return 'LOW'


def parse_date(date_str: str) -> pd.Timestamp:
    """
    Parse date string in DD-MM-YYYY format.
    
    Args:
        date_str: Date string in DD-MM-YYYY format
        
    Returns:
        Parsed datetime
    """
    return pd.to_datetime(date_str, format='%d-%m-%Y', errors='coerce')


def format_currency_inr(amount: float) -> str:
    """
    Format a number as Indian Rupees with appropriate suffix.
    
    Args:
        amount: Numeric amount
        
    Returns:
        Formatted string with INR notation
    """
    if amount >= 1e7:
        return f"₹{amount/1e7:.2f} Cr"
    elif amount >= 1e5:
        return f"₹{amount/1e5:.2f} L"
    elif amount >= 1e3:
        return f"₹{amount/1e3:.2f} K"
    else:
        return f"₹{amount:.0f}"


def calculate_percentile_rank(series: pd.Series) -> pd.Series:
    """
    Calculate percentile rank for each value in series.
    
    Args:
        series: Pandas series of values
        
    Returns:
        Series with percentile ranks (0-100)
    """
    return series.rank(pct=True) * 100


def get_state_code(state_name: str) -> str:
    """
    Get standard state code from state name.
    Uses first 2-3 characters as abbreviation.
    
    Args:
        state_name: Full state name
        
    Returns:
        State abbreviation code
    """
    state_codes = {
        'Andhra Pradesh': 'AP',
        'Arunachal Pradesh': 'AR',
        'Assam': 'AS',
        'Bihar': 'BR',
        'Chhattisgarh': 'CG',
        'Goa': 'GA',
        'Gujarat': 'GJ',
        'Haryana': 'HR',
        'Himachal Pradesh': 'HP',
        'Jharkhand': 'JH',
        'Karnataka': 'KA',
        'Kerala': 'KL',
        'Madhya Pradesh': 'MP',
        'Maharashtra': 'MH',
        'Manipur': 'MN',
        'Meghalaya': 'ML',
        'Mizoram': 'MZ',
        'Nagaland': 'NL',
        'Odisha': 'OR',
        'Punjab': 'PB',
        'Rajasthan': 'RJ',
        'Sikkim': 'SK',
        'Tamil Nadu': 'TN',
        'Telangana': 'TS',
        'Tripura': 'TR',
        'Uttar Pradesh': 'UP',
        'Uttarakhand': 'UK',
        'West Bengal': 'WB',
        'Andaman and Nicobar Islands': 'AN',
        'Chandigarh': 'CH',
        'Dadra and Nagar Haveli': 'DN',
        'Daman and Diu': 'DD',
        'Delhi': 'DL',
        'Jammu and Kashmir': 'JK',
        'Ladakh': 'LA',
        'Lakshadweep': 'LD',
        'Puducherry': 'PY'
    }
    return state_codes.get(state_name, state_name[:2].upper())


def generate_ioc_id(pattern_type: str, index: int) -> str:
    """
    Generate unique IOC identifier.
    
    Args:
        pattern_type: Type of IOC pattern
        index: Sequential index
        
    Returns:
        Unique IOC ID string
    """
    pattern_codes = {
        'Mass Enrollment Spike': 'MES',
        'Demographic Surge': 'DMS',
        'Biometric Churn': 'BIO',
        'Child Ratio Anomaly': 'CRA',
        'Coordinated PIN Spike': 'CPS'
    }
    code = pattern_codes.get(pattern_type, 'UNK')
    return f"IOC-{code}-{index:06d}"


def get_recommended_action(risk_level: str, pattern_type: str) -> str:
    """
    Generate recommended action based on risk level and pattern type.
    
    Args:
        risk_level: Risk category (CRITICAL, HIGH, MEDIUM, LOW)
        pattern_type: Type of detected pattern
        
    Returns:
        Recommended investigation action
    """
    actions = {
        ('CRITICAL', 'Mass Enrollment Spike'): 'URGENT: Escalate to Field Investigation Unit. Suspend operations at affected centers pending review.',
        ('CRITICAL', 'Demographic Surge'): 'URGENT: Cross-verify with source documents. Flag for identity verification audit.',
        ('CRITICAL', 'Biometric Churn'): 'URGENT: Review biometric capture quality. Check for operator collusion patterns.',
        ('CRITICAL', 'Child Ratio Anomaly'): 'URGENT: Verify birth records. Check for ghost enrollment patterns.',
        ('CRITICAL', 'Coordinated PIN Spike'): 'URGENT: Full forensic audit required. Multiple indicators suggest coordinated fraud.',
        ('HIGH', 'Mass Enrollment Spike'): 'HIGH PRIORITY: Schedule field verification within 48 hours.',
        ('HIGH', 'Demographic Surge'): 'HIGH PRIORITY: Sample audit of recent demographic updates.',
        ('HIGH', 'Biometric Churn'): 'HIGH PRIORITY: Operator performance review required.',
        ('HIGH', 'Child Ratio Anomaly'): 'HIGH PRIORITY: Birth certificate verification for recent enrollments.',
        ('HIGH', 'Coordinated PIN Spike'): 'HIGH PRIORITY: Multi-dimensional audit within 72 hours.',
        ('MEDIUM', 'Mass Enrollment Spike'): 'MONITOR: Add to weekly review queue.',
        ('MEDIUM', 'Demographic Surge'): 'MONITOR: Flag for next monthly audit cycle.',
        ('MEDIUM', 'Biometric Churn'): 'MONITOR: Track operator patterns over next 30 days.',
        ('MEDIUM', 'Child Ratio Anomaly'): 'MONITOR: Include in quarterly child enrollment review.',
        ('MEDIUM', 'Coordinated PIN Spike'): 'MONITOR: Establish baseline and track for escalation.',
    }
    
    default_action = 'LOG: Continue monitoring. No immediate action required.'
    return actions.get((risk_level, pattern_type), default_action)


class DataValidator:
    """Validates data integrity for the A-SOC system."""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, 
                          required_columns: list,
                          dataset_name: str) -> tuple:
        """
        Validate that a dataframe has required columns and proper types.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            dataset_name: Name of dataset for error messages
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check for required columns
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"{dataset_name}: Missing columns: {missing_cols}")
        
        # Check for empty dataframe
        if df.empty:
            errors.append(f"{dataset_name}: DataFrame is empty")
        
        # Check for all-null columns
        for col in df.columns:
            if df[col].isna().all():
                errors.append(f"{dataset_name}: Column '{col}' is entirely null")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def get_data_quality_metrics(df: pd.DataFrame) -> dict:
        """
        Calculate data quality metrics for a dataframe.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary of quality metrics
        """
        total_cells = df.size
        null_cells = df.isna().sum().sum()
        
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_cells': total_cells,
            'null_cells': null_cells,
            'null_percentage': round((null_cells / total_cells) * 100, 2) if total_cells > 0 else 0,
            'duplicate_rows': df.duplicated().sum(),
            'memory_mb': round(df.memory_usage(deep=True).sum() / 1e6, 2)
        }
