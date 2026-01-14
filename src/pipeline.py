"""
A-SOC Main Pipeline
====================
Orchestrates the complete Aadhaar fraud detection pipeline.

Pipeline Steps:
1. Load and clean data
2. Merge datasets
3. Engineer features
4. Calculate risk scores
5. Detect IOCs
6. Generate outputs

All outputs are deterministic with fixed random seed = 42.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from cleaning import DataCleaner, get_merged_data
from features import FeatureEngineer, engineer_features
from risk_scoring import RiskScorer, calculate_risk_scores
from ioc_detection import IOCDetector, detect_iocs


def run_pipeline(data_dir: str, output_dir: str, verbose: bool = True) -> dict:
    """
    Run the complete A-SOC pipeline.
    
    Args:
        data_dir: Path to data directory
        output_dir: Path to output directory
        verbose: Print progress messages
        
    Returns:
        Dictionary with pipeline results and statistics
    """
    start_time = datetime.now()
    
    if verbose:
        print("=" * 70)
        print("A-SOC THREAT INTELLIGENCE PIPELINE")
        print("Aadhaar Security Operations Center - Fraud Detection System")
        print("=" * 70)
        print(f"\nPipeline started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Random seed: 42 (deterministic)")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {
        'start_time': start_time,
        'data_dir': data_dir,
        'output_dir': output_dir
    }
    
    # =========================================================================
    # STEP 1: Load and Clean Data
    # =========================================================================
    if verbose:
        print("\n" + "-" * 70)
        print("STEP 1: Loading and Cleaning Data")
        print("-" * 70)
    
    cleaner = DataCleaner(data_dir)
    enrollment_df, demographic_df, biometric_df = cleaner.load_all_data()
    
    results['raw_data'] = {
        'enrollment_records': len(enrollment_df),
        'demographic_records': len(demographic_df),
        'biometric_records': len(biometric_df),
        'enrollment_date_range': (str(enrollment_df['date'].min()), str(enrollment_df['date'].max())),
        'states': enrollment_df['state'].nunique(),
        'districts': enrollment_df['district'].nunique(),
        'pincodes': enrollment_df['pincode'].nunique()
    }
    
    # =========================================================================
    # STEP 2: Merge Datasets
    # =========================================================================
    if verbose:
        print("\n" + "-" * 70)
        print("STEP 2: Merging Datasets at PIN Level")
        print("-" * 70)
    
    # PIN-level aggregation for risk scoring
    merged_pin = cleaner.merge_datasets(enrollment_df, demographic_df, biometric_df, 'pin')
    
    # Time-series aggregation for temporal analysis
    merged_daily = cleaner.merge_datasets(enrollment_df, demographic_df, biometric_df, 'pin_date')
    
    # State-level aggregation for geographic analysis
    merged_state = cleaner.merge_datasets(enrollment_df, demographic_df, biometric_df, 'state')
    
    results['merged_data'] = {
        'pin_level_records': len(merged_pin),
        'daily_records': len(merged_daily),
        'state_records': len(merged_state)
    }
    
    # =========================================================================
    # STEP 3: Engineer Features
    # =========================================================================
    if verbose:
        print("\n" + "-" * 70)
        print("STEP 3: Feature Engineering")
        print("-" * 70)
    
    engineer = FeatureEngineer()
    df_features = engineer.engineer_all_features(merged_pin)
    
    results['features'] = {
        'total_features': len(df_features.columns),
        'national_medians': engineer.national_medians
    }
    
    # =========================================================================
    # STEP 4: Calculate Risk Scores
    # =========================================================================
    if verbose:
        print("\n" + "-" * 70)
        print("STEP 4: Risk Scoring")
        print("-" * 70)
    
    scorer = RiskScorer()
    df_scored = scorer.calculate_composite_risk_score(df_features)
    df_scored = scorer.add_risk_explanations(df_scored)
    
    risk_summary = scorer.get_risk_summary(df_scored)
    results['risk_scoring'] = risk_summary
    
    # =========================================================================
    # STEP 5: Detect IOCs
    # =========================================================================
    if verbose:
        print("\n" + "-" * 70)
        print("STEP 5: IOC Detection")
        print("-" * 70)
    
    detector = IOCDetector()
    ioc_catalogue = detector.detect_all_iocs(df_scored)
    alerts = detector.generate_alerts(ioc_catalogue, min_risk_level='MEDIUM')
    
    ioc_summary = detector.get_ioc_summary(ioc_catalogue)
    results['ioc_detection'] = ioc_summary
    
    # =========================================================================
    # STEP 6: Generate Outputs
    # =========================================================================
    if verbose:
        print("\n" + "-" * 70)
        print("STEP 6: Generating Output Files")
        print("-" * 70)
    
    # Risk Scores CSV
    risk_output_cols = [
        'pincode', 'state', 'district',
        'total_enrollments', 'total_demo_updates', 'total_bio_updates',
        'age_0_5', 'age_5_17', 'age_18_greater',
        'child_ratio', 'update_ratio', 'bio_recapture_ratio',
        'enrollment_velocity', 'update_velocity', 'bio_velocity',
        'child_ratio_zscore', 'update_ratio_zscore', 'bio_recapture_ratio_zscore',
        'risk_enrollment_velocity', 'risk_update_velocity', 
        'risk_demographic_anomaly', 'risk_geographic_outlier', 'risk_temporal_spike',
        'risk_score', 'risk_level', 'risk_factors'
    ]
    
    # Filter to existing columns
    risk_output_cols = [col for col in risk_output_cols if col in df_scored.columns]
    risk_df = df_scored[risk_output_cols].copy()
    risk_df = risk_df.sort_values('risk_score', ascending=False)
    
    risk_output_path = output_path / 'risk_scores.csv'
    risk_df.to_csv(risk_output_path, index=False)
    if verbose:
        print(f"  ✓ Risk scores saved: {risk_output_path}")
    
    # IOC Catalogue CSV
    if not ioc_catalogue.empty:
        ioc_output_path = output_path / 'ioc_catalogue.csv'
        ioc_catalogue.to_csv(ioc_output_path, index=False)
        if verbose:
            print(f"  ✓ IOC catalogue saved: {ioc_output_path}")
    
    # Alerts CSV
    if not alerts.empty:
        alerts_output_path = output_path / 'alerts.csv'
        alerts.to_csv(alerts_output_path, index=False)
        if verbose:
            print(f"  ✓ Alerts saved: {alerts_output_path}")
    
    # State-level summary for Tableau
    state_summary = merged_state.copy()
    if 'total_enrollments' in state_summary.columns:
        # Calculate state-level risk metrics
        state_risk = df_scored.groupby('state').agg({
            'risk_score': ['mean', 'max', 'std'],
            'pincode': 'count'
        }).reset_index()
        state_risk.columns = ['state', 'avg_risk_score', 'max_risk_score', 'risk_score_std', 'pin_count']
        
        # Count high-risk PINs per state
        high_risk_counts = df_scored[df_scored['risk_level'].isin(['CRITICAL', 'HIGH'])].groupby('state').size().reset_index(name='high_risk_pins')
        state_risk = state_risk.merge(high_risk_counts, on='state', how='left')
        state_risk['high_risk_pins'] = state_risk['high_risk_pins'].fillna(0).astype(int)
        
        state_output_path = output_path / 'state_summary.csv'
        state_risk.to_csv(state_output_path, index=False)
        if verbose:
            print(f"  ✓ State summary saved: {state_output_path}")
    
    # District-level summary
    district_risk = df_scored.groupby(['state', 'district']).agg({
        'risk_score': ['mean', 'max', 'count'],
        'total_enrollments': 'sum',
        'total_demo_updates': 'sum',
        'total_bio_updates': 'sum'
    }).reset_index()
    district_risk.columns = ['state', 'district', 'avg_risk_score', 'max_risk_score', 'pin_count',
                             'total_enrollments', 'total_demo_updates', 'total_bio_updates']
    
    district_output_path = output_path / 'district_summary.csv'
    district_risk.to_csv(district_output_path, index=False)
    if verbose:
        print(f"  ✓ District summary saved: {district_output_path}")
    
    # Daily time-series for temporal charts
    if 'date' in merged_daily.columns:
        daily_summary = merged_daily.groupby('date').agg({
            'total_enrollments': 'sum',
            'total_demo_updates': 'sum',
            'total_bio_updates': 'sum',
            'pincode': 'nunique'
        }).reset_index()
        daily_summary.columns = ['date', 'total_enrollments', 'total_demo_updates', 
                                  'total_bio_updates', 'active_pins']
        
        daily_output_path = output_path / 'daily_summary.csv'
        daily_summary.to_csv(daily_output_path, index=False)
        if verbose:
            print(f"  ✓ Daily summary saved: {daily_output_path}")
    
    # =========================================================================
    # Pipeline Complete
    # =========================================================================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    results['end_time'] = end_time
    results['duration_seconds'] = duration
    
    if verbose:
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)
        print(f"\nDuration: {duration:.2f} seconds")
        print(f"\nSummary:")
        print(f"  Total PIN codes analyzed: {len(df_scored):,}")
        print(f"  Critical risk PINs: {risk_summary['risk_distribution']['critical']:,}")
        print(f"  High risk PINs: {risk_summary['risk_distribution']['high']:,}")
        print(f"  Total IOCs detected: {ioc_summary['total_iocs']:,}")
        print(f"  Active alerts: {len(alerts):,}")
        print(f"\nOutput files saved to: {output_dir}")
    
    return results


def main():
    """Main entry point for the pipeline."""
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    data_dir = os.path.join(project_root, 'data')
    output_dir = os.path.join(project_root, 'outputs')
    
    # Run the pipeline
    results = run_pipeline(data_dir, output_dir, verbose=True)
    
    return results


if __name__ == "__main__":
    main()
