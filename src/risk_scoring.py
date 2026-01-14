"""
A-SOC Risk Scoring Module
==========================
Calculates composite risk scores as specified in claude.md Section 5.

Risk Components (0-10 scale):
- Enrollment Velocity: 30%
- Update Velocity: 25%
- Demographic Anomaly (Z): 20%
- Geographic Outlier: 15%
- Temporal Spike: 10%

Risk Categories:
- Critical: >= 8
- High: 6 - 7.99
- Medium: 4 - 5.99
- Low: < 4
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional
import warnings

warnings.filterwarnings('ignore')

# Fixed random seed for reproducibility
np.random.seed(42)


class RiskScorer:
    """
    Calculates composite risk scores for PIN codes.
    
    The risk model is transparent, explainable, and deterministic.
    All weights and thresholds are locked per claude.md specification.
    """
    
    # Locked weights per specification
    WEIGHTS = {
        'enrollment_velocity': 0.30,
        'update_velocity': 0.25,
        'demographic_anomaly': 0.20,
        'geographic_outlier': 0.15,
        'temporal_spike': 0.10
    }
    
    # Risk category thresholds
    RISK_THRESHOLDS = {
        'CRITICAL': 8.0,
        'HIGH': 6.0,
        'MEDIUM': 4.0,
        'LOW': 0.0
    }
    
    def __init__(self):
        """Initialize the RiskScorer."""
        self.component_stats = {}
    
    @staticmethod
    def normalize_to_10(series: pd.Series, percentile_cap: float = 99) -> pd.Series:
        """
        Normalize a series to 0-10 scale using percentile-based normalization.
        
        Args:
            series: Input series
            percentile_cap: Percentile to use as maximum (avoids extreme outliers)
            
        Returns:
            Normalized series (0-10 scale)
        """
        if series.max() == series.min():
            return pd.Series([5.0] * len(series), index=series.index)
        
        # Use percentile cap to handle extreme outliers
        cap_value = series.quantile(percentile_cap / 100)
        if cap_value <= 0:
            cap_value = series.max()
        
        # Min-max normalization with cap
        normalized = (series.clip(0, cap_value) / cap_value) * 10
        return normalized.clip(0, 10)
    
    def calculate_enrollment_velocity_component(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate enrollment velocity risk component (0-10).
        
        High velocity indicates unusual enrollment activity.
        
        Args:
            df: DataFrame with enrollment_velocity column
            
        Returns:
            Risk component series
        """
        if 'enrollment_velocity' not in df.columns:
            return pd.Series([0.0] * len(df), index=df.index)
        
        # Normalize velocity to 0-10 scale
        component = self.normalize_to_10(df['enrollment_velocity'])
        
        self.component_stats['enrollment_velocity'] = {
            'mean': component.mean(),
            'std': component.std(),
            'max': component.max()
        }
        
        return component
    
    def calculate_update_velocity_component(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate update velocity risk component (0-10).
        
        High update velocity indicates unusual demographic update activity.
        
        Args:
            df: DataFrame with update_velocity column
            
        Returns:
            Risk component series
        """
        if 'update_velocity' not in df.columns:
            return pd.Series([0.0] * len(df), index=df.index)
        
        component = self.normalize_to_10(df['update_velocity'])
        
        self.component_stats['update_velocity'] = {
            'mean': component.mean(),
            'std': component.std(),
            'max': component.max()
        }
        
        return component
    
    def calculate_demographic_anomaly_component(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate demographic anomaly risk component (0-10).
        
        Based on Z-scores of child ratio, update ratio, and bio recapture ratio.
        
        Args:
            df: DataFrame with Z-score columns
            
        Returns:
            Risk component series
        """
        zscore_cols = ['child_ratio_zscore', 'update_ratio_zscore', 'bio_recapture_ratio_zscore']
        existing_cols = [col for col in zscore_cols if col in df.columns]
        
        if not existing_cols:
            return pd.Series([0.0] * len(df), index=df.index)
        
        # Combine Z-scores using absolute values (high positive OR negative is anomalous)
        combined_zscore = df[existing_cols].abs().mean(axis=1)
        
        # Map Z-score to 0-10 scale
        # Z-score of 3+ should map to high risk (7-10)
        # Z-score of 0 should map to low risk (0-2)
        component = (combined_zscore / 5 * 10).clip(0, 10)
        
        self.component_stats['demographic_anomaly'] = {
            'mean': component.mean(),
            'std': component.std(),
            'max': component.max()
        }
        
        return component
    
    def calculate_geographic_outlier_component(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate geographic outlier risk component (0-10).
        
        Args:
            df: DataFrame with geographic_outlier_score column
            
        Returns:
            Risk component series
        """
        if 'geographic_outlier_score' not in df.columns:
            return pd.Series([0.0] * len(df), index=df.index)
        
        component = df['geographic_outlier_score'].clip(0, 10)
        
        self.component_stats['geographic_outlier'] = {
            'mean': component.mean(),
            'std': component.std(),
            'max': component.max()
        }
        
        return component
    
    def calculate_temporal_spike_component(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate temporal spike risk component (0-10).
        
        Args:
            df: DataFrame with temporal_spike_score column
            
        Returns:
            Risk component series
        """
        if 'temporal_spike_score' not in df.columns:
            return pd.Series([0.0] * len(df), index=df.index)
        
        component = df['temporal_spike_score'].clip(0, 10)
        
        self.component_stats['temporal_spike'] = {
            'mean': component.mean(),
            'std': component.std(),
            'max': component.max()
        }
        
        return component
    
    def calculate_composite_risk_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite risk score from all components.
        
        Formula (from claude.md):
        Risk_Score = 
            (Enroll_Velocity * 0.30) +
            (Update_Velocity * 0.25) +
            (Demo_Z * 0.20) +
            (Geo_Outlier * 0.15) +
            (Time_Spike * 0.10)
        
        Args:
            df: DataFrame with all feature columns
            
        Returns:
            DataFrame with risk scores added
        """
        df = df.copy()
        
        print("Calculating risk components...")
        
        # Calculate individual components
        df['risk_enrollment_velocity'] = self.calculate_enrollment_velocity_component(df)
        print(f"  ✓ Enrollment velocity component (weight: {self.WEIGHTS['enrollment_velocity']})")
        
        df['risk_update_velocity'] = self.calculate_update_velocity_component(df)
        print(f"  ✓ Update velocity component (weight: {self.WEIGHTS['update_velocity']})")
        
        df['risk_demographic_anomaly'] = self.calculate_demographic_anomaly_component(df)
        print(f"  ✓ Demographic anomaly component (weight: {self.WEIGHTS['demographic_anomaly']})")
        
        df['risk_geographic_outlier'] = self.calculate_geographic_outlier_component(df)
        print(f"  ✓ Geographic outlier component (weight: {self.WEIGHTS['geographic_outlier']})")
        
        df['risk_temporal_spike'] = self.calculate_temporal_spike_component(df)
        print(f"  ✓ Temporal spike component (weight: {self.WEIGHTS['temporal_spike']})")
        
        # Calculate composite score
        df['risk_score'] = (
            df['risk_enrollment_velocity'] * self.WEIGHTS['enrollment_velocity'] +
            df['risk_update_velocity'] * self.WEIGHTS['update_velocity'] +
            df['risk_demographic_anomaly'] * self.WEIGHTS['demographic_anomaly'] +
            df['risk_geographic_outlier'] * self.WEIGHTS['geographic_outlier'] +
            df['risk_temporal_spike'] * self.WEIGHTS['temporal_spike']
        )
        
        # Clip to 0-10 range
        df['risk_score'] = df['risk_score'].clip(0, 10)
        
        # Assign risk categories
        df['risk_level'] = self.assign_risk_categories(df['risk_score'])
        
        print(f"\n  Composite risk score calculated")
        print(f"  Risk distribution:")
        print(f"    Critical (≥8): {(df['risk_level'] == 'CRITICAL').sum():,}")
        print(f"    High (6-8): {(df['risk_level'] == 'HIGH').sum():,}")
        print(f"    Medium (4-6): {(df['risk_level'] == 'MEDIUM').sum():,}")
        print(f"    Low (<4): {(df['risk_level'] == 'LOW').sum():,}")
        
        return df
    
    def assign_risk_categories(self, risk_scores: pd.Series) -> pd.Series:
        """
        Assign risk categories based on score thresholds.
        
        Categories:
        - Critical: >= 8
        - High: 6 - 7.99
        - Medium: 4 - 5.99
        - Low: < 4
        
        Args:
            risk_scores: Series of risk scores
            
        Returns:
            Series of risk category labels
        """
        conditions = [
            risk_scores >= self.RISK_THRESHOLDS['CRITICAL'],
            risk_scores >= self.RISK_THRESHOLDS['HIGH'],
            risk_scores >= self.RISK_THRESHOLDS['MEDIUM'],
            risk_scores >= self.RISK_THRESHOLDS['LOW']
        ]
        choices = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        
        return pd.Series(
            np.select(conditions, choices, default='LOW'),
            index=risk_scores.index
        )
    
    def get_top_risk_factors(self, row: pd.Series) -> str:
        """
        Identify the top contributing risk factors for a single record.
        
        Args:
            row: Single row from the scored DataFrame
            
        Returns:
            String describing top risk factors
        """
        components = {
            'Enrollment Velocity': row.get('risk_enrollment_velocity', 0) * self.WEIGHTS['enrollment_velocity'],
            'Update Velocity': row.get('risk_update_velocity', 0) * self.WEIGHTS['update_velocity'],
            'Demographic Anomaly': row.get('risk_demographic_anomaly', 0) * self.WEIGHTS['demographic_anomaly'],
            'Geographic Outlier': row.get('risk_geographic_outlier', 0) * self.WEIGHTS['geographic_outlier'],
            'Temporal Spike': row.get('risk_temporal_spike', 0) * self.WEIGHTS['temporal_spike']
        }
        
        # Sort by contribution
        sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 2 contributors
        top_factors = [f"{name} ({value:.2f})" for name, value in sorted_components[:2] if value > 0.1]
        
        return "; ".join(top_factors) if top_factors else "No significant factors"
    
    def add_risk_explanations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add human-readable risk explanations to each record.
        
        Args:
            df: DataFrame with risk scores
            
        Returns:
            DataFrame with risk_explanation column added
        """
        df = df.copy()
        
        explanations = []
        for idx, row in df.iterrows():
            explanation = self.get_top_risk_factors(row)
            explanations.append(explanation)
        
        df['risk_factors'] = explanations
        
        return df
    
    def get_risk_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for risk scores.
        
        Args:
            df: DataFrame with risk scores
            
        Returns:
            Dictionary of summary statistics
        """
        summary = {
            'total_records': len(df),
            'risk_distribution': {
                'critical': int((df['risk_level'] == 'CRITICAL').sum()),
                'high': int((df['risk_level'] == 'HIGH').sum()),
                'medium': int((df['risk_level'] == 'MEDIUM').sum()),
                'low': int((df['risk_level'] == 'LOW').sum())
            },
            'risk_score_stats': {
                'mean': float(df['risk_score'].mean()),
                'median': float(df['risk_score'].median()),
                'std': float(df['risk_score'].std()),
                'min': float(df['risk_score'].min()),
                'max': float(df['risk_score'].max()),
                'p95': float(df['risk_score'].quantile(0.95)),
                'p99': float(df['risk_score'].quantile(0.99))
            },
            'component_stats': self.component_stats
        }
        
        return summary
    
    def get_high_risk_records(self, df: pd.DataFrame, min_level: str = 'HIGH') -> pd.DataFrame:
        """
        Filter to high-risk records only.
        
        Args:
            df: DataFrame with risk scores
            min_level: Minimum risk level to include ('CRITICAL', 'HIGH', 'MEDIUM')
            
        Returns:
            Filtered DataFrame
        """
        if min_level == 'CRITICAL':
            return df[df['risk_level'] == 'CRITICAL'].copy()
        elif min_level == 'HIGH':
            return df[df['risk_level'].isin(['CRITICAL', 'HIGH'])].copy()
        elif min_level == 'MEDIUM':
            return df[df['risk_level'].isin(['CRITICAL', 'HIGH', 'MEDIUM'])].copy()
        else:
            return df.copy()


def calculate_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to calculate risk scores.
    
    Args:
        df: DataFrame with engineered features
        
    Returns:
        DataFrame with risk scores
    """
    scorer = RiskScorer()
    df_scored = scorer.calculate_composite_risk_score(df)
    df_scored = scorer.add_risk_explanations(df_scored)
    return df_scored


if __name__ == "__main__":
    # Test the module
    import os
    import sys
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    
    from cleaning import get_merged_data
    from features import engineer_features
    
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    print("=" * 60)
    print("A-SOC Risk Scoring Module Test")
    print("=" * 60)
    
    # Load and process data
    df = get_merged_data(data_dir, aggregation_level='pin')
    df = engineer_features(df)
    
    # Calculate risk scores
    scorer = RiskScorer()
    df_scored = scorer.calculate_composite_risk_score(df)
    df_scored = scorer.add_risk_explanations(df_scored)
    
    print("\n" + "=" * 60)
    print("Risk Summary")
    print("=" * 60)
    
    summary = scorer.get_risk_summary(df_scored)
    print(f"\nTotal Records: {summary['total_records']:,}")
    print(f"\nRisk Distribution:")
    for level, count in summary['risk_distribution'].items():
        pct = count / summary['total_records'] * 100
        print(f"  {level.upper()}: {count:,} ({pct:.2f}%)")
    
    print(f"\nRisk Score Statistics:")
    for stat, value in summary['risk_score_stats'].items():
        print(f"  {stat}: {value:.4f}")
    
    # Show top 10 highest risk
    print("\n" + "=" * 60)
    print("Top 10 Highest Risk PIN Codes")
    print("=" * 60)
    
    top_risk = df_scored.nlargest(10, 'risk_score')[
        ['pincode', 'state', 'district', 'risk_score', 'risk_level', 'risk_factors']
    ]
    print(top_risk.to_string(index=False))
