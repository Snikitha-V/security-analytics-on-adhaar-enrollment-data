"""
A-SOC Feature Engineering Module
=================================
Calculates all derived metrics, ratios, velocities, and Z-scores
as specified in claude.md Section 4.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# Fixed random seed for reproducibility
np.random.seed(42)


class FeatureEngineer:
    """
    Calculates all derived features for the A-SOC system.
    
    Features are calculated exactly as specified in claude.md:
    - Core Metrics (totals)
    - Ratios (child ratio, update ratio, bio recapture ratio)
    - Velocity Metrics (enrollment, update, bio velocities)
    - Statistical Anomalies (Z-scores clipped to ±5)
    """
    
    def __init__(self):
        """Initialize the FeatureEngineer."""
        self.national_medians = {}
    
    @staticmethod
    def safe_divide(numerator: pd.Series, denominator: pd.Series, default: float = 0.0) -> pd.Series:
        """
        Safely divide two series, handling division by zero.
        
        Args:
            numerator: Numerator series
            denominator: Denominator series
            default: Default value for division by zero
            
        Returns:
            Result series with safe division
        """
        result = numerator / denominator
        result = result.replace([np.inf, -np.inf], default)
        result = result.fillna(default)
        return result
    
    @staticmethod
    def calculate_zscore(series: pd.Series, clip_limit: float = 5.0) -> pd.Series:
        """
        Calculate Z-scores for a series, clipped to ±limit.
        
        Args:
            series: Input series
            clip_limit: Maximum absolute Z-score value
            
        Returns:
            Clipped Z-score series
        """
        if series.std() == 0:
            return pd.Series([0.0] * len(series), index=series.index)
        
        zscore = (series - series.mean()) / series.std()
        return zscore.clip(-clip_limit, clip_limit)
    
    def calculate_core_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate core metrics (totals) from raw data.
        
        Metrics:
        - total_enrollments = age_0_5 + age_5_17 + age_18_greater
        - total_demo_updates = demo_age_5_17 + demo_age_18_greater
        - total_bio_updates = bio_age_5_17 + bio_age_18_greater
        
        Args:
            df: Input DataFrame with raw data
            
        Returns:
            DataFrame with core metrics added
        """
        df = df.copy()
        
        # Enrollment totals (if columns exist)
        if 'age_0_5' in df.columns:
            df['total_enrollments'] = (
                df['age_0_5'].fillna(0) + 
                df['age_5_17'].fillna(0) + 
                df['age_18_greater'].fillna(0)
            )
        
        # Demographic update totals
        if 'demo_age_5_17' in df.columns:
            df['total_demo_updates'] = (
                df['demo_age_5_17'].fillna(0) + 
                df['demo_age_18_greater'].fillna(0)
            )
        
        # Biometric update totals
        if 'bio_age_5_17' in df.columns:
            df['total_bio_updates'] = (
                df['bio_age_5_17'].fillna(0) + 
                df['bio_age_18_greater'].fillna(0)
            )
        
        return df
    
    def calculate_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ratio metrics.
        
        Ratios:
        - child_ratio = age_0_5 / total_enrollments
        - update_ratio = total_demo_updates / total_enrollments
        - bio_recapture_ratio = total_bio_updates / total_enrollments
        
        Args:
            df: Input DataFrame with core metrics
            
        Returns:
            DataFrame with ratios added
        """
        df = df.copy()
        
        # Child Ratio
        if 'age_0_5' in df.columns and 'total_enrollments' in df.columns:
            df['child_ratio'] = self.safe_divide(
                df['age_0_5'], 
                df['total_enrollments']
            )
        
        # Update Ratio (demographic updates relative to enrollments)
        if 'total_demo_updates' in df.columns and 'total_enrollments' in df.columns:
            df['update_ratio'] = self.safe_divide(
                df['total_demo_updates'], 
                df['total_enrollments']
            )
        
        # Biometric Recapture Ratio
        if 'total_bio_updates' in df.columns and 'total_enrollments' in df.columns:
            df['bio_recapture_ratio'] = self.safe_divide(
                df['total_bio_updates'], 
                df['total_enrollments']
            )
        
        # NEW: Adult Ratio (inverse of child ratio - for ghost enrollment detection)
        if 'age_18_greater' in df.columns and 'total_enrollments' in df.columns:
            df['adult_ratio'] = self.safe_divide(
                df['age_18_greater'], 
                df['total_enrollments']
            )
        
        # NEW: Youth Ratio (age 5-17)
        if 'age_5_17' in df.columns and 'total_enrollments' in df.columns:
            df['youth_ratio'] = self.safe_divide(
                df['age_5_17'], 
                df['total_enrollments']
            )
        
        # NEW: Activity Intensity (total activity per enrollment)
        if all(col in df.columns for col in ['total_demo_updates', 'total_bio_updates', 'total_enrollments']):
            df['activity_intensity'] = self.safe_divide(
                df['total_demo_updates'] + df['total_bio_updates'],
                df['total_enrollments']
            )
        
        return df
    
    def calculate_national_medians(self, df: pd.DataFrame) -> dict:
        """
        Calculate national median values for velocity calculations.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary of national medians
        """
        medians = {}
        
        if 'total_enrollments' in df.columns:
            medians['enrollment'] = df['total_enrollments'].median()
            if medians['enrollment'] == 0:
                medians['enrollment'] = 1  # Avoid division by zero
        
        if 'total_demo_updates' in df.columns:
            medians['demo_updates'] = df['total_demo_updates'].median()
            if medians['demo_updates'] == 0:
                medians['demo_updates'] = 1
        
        if 'total_bio_updates' in df.columns:
            medians['bio_updates'] = df['total_bio_updates'].median()
            if medians['bio_updates'] == 0:
                medians['bio_updates'] = 1
        
        self.national_medians = medians
        return medians
    
    def calculate_velocities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate velocity metrics relative to national medians.
        
        Velocities:
        - enrollment_velocity = PIN_Total_Enrollments / National_Median_Enrollments
        - update_velocity = PIN_Total_Updates / National_Median_Updates
        - bio_velocity = PIN_Total_Bio_Updates / National_Median_Bio
        
        Args:
            df: Input DataFrame with core metrics
            
        Returns:
            DataFrame with velocities added
        """
        df = df.copy()
        
        # Calculate national medians if not already done
        if not self.national_medians:
            self.calculate_national_medians(df)
        
        # Enrollment Velocity
        if 'total_enrollments' in df.columns and 'enrollment' in self.national_medians:
            df['enrollment_velocity'] = self.safe_divide(
                df['total_enrollments'],
                self.national_medians['enrollment']
            )
        
        # Update Velocity
        if 'total_demo_updates' in df.columns and 'demo_updates' in self.national_medians:
            df['update_velocity'] = self.safe_divide(
                df['total_demo_updates'],
                self.national_medians['demo_updates']
            )
        
        # Biometric Velocity
        if 'total_bio_updates' in df.columns and 'bio_updates' in self.national_medians:
            df['bio_velocity'] = self.safe_divide(
                df['total_bio_updates'],
                self.national_medians['bio_updates']
            )
        
        return df
    
    def calculate_zscores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Z-scores for ratio metrics, clipped to ±5.
        
        Z-scores applied to:
        - child_ratio_zscore
        - update_ratio_zscore
        - bio_recapture_ratio_zscore
        
        Args:
            df: Input DataFrame with ratios
            
        Returns:
            DataFrame with Z-scores added
        """
        df = df.copy()
        
        # Child Ratio Z-score
        if 'child_ratio' in df.columns:
            df['child_ratio_zscore'] = self.calculate_zscore(df['child_ratio'])
        
        # Update Ratio Z-score
        if 'update_ratio' in df.columns:
            df['update_ratio_zscore'] = self.calculate_zscore(df['update_ratio'])
        
        # Bio Recapture Ratio Z-score
        if 'bio_recapture_ratio' in df.columns:
            df['bio_recapture_ratio_zscore'] = self.calculate_zscore(df['bio_recapture_ratio'])
        
        return df
    
    def calculate_geographic_outlier_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate geographic outlier score based on deviation from district/state norms.
        
        A PIN is a geographic outlier if its metrics deviate significantly
        from other PINs in the same district or state.
        
        Args:
            df: Input DataFrame with velocities
            
        Returns:
            DataFrame with geographic outlier scores
        """
        df = df.copy()
        
        if 'district' not in df.columns or 'enrollment_velocity' not in df.columns:
            df['geographic_outlier_score'] = 0.0
            return df
        
        # Calculate district-level medians
        district_medians = df.groupby('district')['enrollment_velocity'].transform('median')
        district_stds = df.groupby('district')['enrollment_velocity'].transform('std').fillna(1)
        district_stds = district_stds.replace(0, 1)
        
        # Geographic outlier = deviation from district median
        deviation = np.abs(df['enrollment_velocity'] - district_medians) / district_stds
        
        # Normalize to 0-10 scale
        max_dev = deviation.quantile(0.99)  # Use 99th percentile to avoid extreme outliers
        if max_dev > 0:
            df['geographic_outlier_score'] = (deviation / max_dev * 10).clip(0, 10)
        else:
            df['geographic_outlier_score'] = 0.0
        
        return df
    
    def calculate_temporal_spike_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate temporal spike score based on sudden changes over time.
        
        For PIN-level data without date, this uses enrollment variance.
        For time-series data, this would detect week-over-week spikes.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with temporal spike scores
        """
        df = df.copy()
        
        if 'date' in df.columns and 'pincode' in df.columns:
            # Time-series spike detection
            # Group by PIN and calculate rolling variance
            df_sorted = df.sort_values(['pincode', 'date'])
            
            # Calculate 7-day rolling statistics per PIN
            df_sorted['rolling_mean'] = df_sorted.groupby('pincode')['total_enrollments'].transform(
                lambda x: x.rolling(7, min_periods=1).mean()
            )
            df_sorted['rolling_std'] = df_sorted.groupby('pincode')['total_enrollments'].transform(
                lambda x: x.rolling(7, min_periods=1).std().fillna(0)
            )
            
            # Spike = current value significantly above rolling mean
            deviation = (df_sorted['total_enrollments'] - df_sorted['rolling_mean']) / (df_sorted['rolling_std'] + 1)
            
            # Normalize to 0-10 scale
            max_dev = deviation.abs().quantile(0.99)
            if max_dev > 0:
                df_sorted['temporal_spike_score'] = (deviation.abs() / max_dev * 10).clip(0, 10)
            else:
                df_sorted['temporal_spike_score'] = 0.0
            
            # Drop helper columns
            df_sorted = df_sorted.drop(columns=['rolling_mean', 'rolling_std'])
            return df_sorted
        
        else:
            # For aggregated data without dates, use velocity variance
            if 'enrollment_velocity' in df.columns:
                # High velocity = potential temporal spike
                velocity_scaled = df['enrollment_velocity'] / df['enrollment_velocity'].quantile(0.99)
                df['temporal_spike_score'] = velocity_scaled.clip(0, 10)
            else:
                df['temporal_spike_score'] = 0.0
        
        return df
    
    def engineer_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps in correct order.
        
        Order:
        1. Core Metrics
        2. Ratios
        3. National Medians
        4. Velocities
        5. Z-scores
        6. Geographic Outlier Score
        7. Temporal Spike Score
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with all features
        """
        print("Engineering features...")
        
        # Step 1: Core Metrics
        df = self.calculate_core_metrics(df)
        print("  ✓ Core metrics calculated")
        
        # Step 2: Ratios
        df = self.calculate_ratios(df)
        print("  ✓ Ratios calculated")
        
        # Step 3: National Medians
        self.calculate_national_medians(df)
        print(f"  ✓ National medians: {self.national_medians}")
        
        # Step 4: Velocities
        df = self.calculate_velocities(df)
        print("  ✓ Velocities calculated")
        
        # Step 5: Z-scores
        df = self.calculate_zscores(df)
        print("  ✓ Z-scores calculated (clipped to ±5)")
        
        # Step 6: Geographic Outlier Score
        df = self.calculate_geographic_outlier_score(df)
        print("  ✓ Geographic outlier scores calculated")
        
        # Step 7: Temporal Spike Score
        df = self.calculate_temporal_spike_score(df)
        print("  ✓ Temporal spike scores calculated")
        
        return df
    
    def get_feature_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary statistics for all engineered features.
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            Summary DataFrame
        """
        feature_cols = [
            'total_enrollments', 'total_demo_updates', 'total_bio_updates',
            'child_ratio', 'update_ratio', 'bio_recapture_ratio',
            'enrollment_velocity', 'update_velocity', 'bio_velocity',
            'child_ratio_zscore', 'update_ratio_zscore', 'bio_recapture_ratio_zscore',
            'geographic_outlier_score', 'temporal_spike_score'
        ]
        
        existing_cols = [col for col in feature_cols if col in df.columns]
        
        summary = df[existing_cols].describe().T
        summary['non_zero_count'] = (df[existing_cols] != 0).sum()
        summary['zero_count'] = (df[existing_cols] == 0).sum()
        
        return summary


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to engineer all features.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with all engineered features
    """
    engineer = FeatureEngineer()
    return engineer.engineer_all_features(df)


if __name__ == "__main__":
    # Test the module
    import os
    import sys
    
    # Add src to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    
    from cleaning import get_merged_data
    
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    print("=" * 60)
    print("A-SOC Feature Engineering Module Test")
    print("=" * 60)
    
    # Load merged data
    df = get_merged_data(data_dir, aggregation_level='pin')
    
    # Engineer features
    engineer = FeatureEngineer()
    df_features = engineer.engineer_all_features(df)
    
    print("\n" + "=" * 60)
    print("Feature Summary")
    print("=" * 60)
    
    summary = engineer.get_feature_summary(df_features)
    print(summary.to_string())
    
    print(f"\nFinal DataFrame shape: {df_features.shape}")
    print(f"Columns: {list(df_features.columns)}")
