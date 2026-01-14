"""
A-SOC IOC Detection Module
===========================
Detects Indicators of Compromise (IOCs) for Aadhaar fraud patterns
as specified in claude.md Section 6.

IOC Patterns (LOCKED):
1. Mass Enrollment Spike: >400% increase in <7 days
2. Demographic Surge: >3× median updates
3. Biometric Churn: >30% recapture ratio
4. Child Ratio Anomaly: Z-score > 3
5. Coordinated PIN Spike: High enroll + demo + bio simultaneously
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# Fixed random seed for reproducibility
np.random.seed(42)


class IOCDetector:
    """
    Detects fraud Indicators of Compromise (IOCs) based on locked rules.
    
    All detection thresholds are fixed per claude.md specification.
    No machine learning - pure rule-based detection for explainability.
    """
    
    # IOC pattern definitions (LOCKED)
    IOC_PATTERNS = {
        'MES': {
            'name': 'Mass Enrollment Spike',
            'description': 'Abnormal surge in enrollments over short period',
            'threshold': 4.0,  # 400% increase
            'window_days': 7
        },
        'DMS': {
            'name': 'Demographic Surge',
            'description': 'Excessive demographic updates relative to median',
            'threshold': 3.0,  # 3x median
        },
        'BIO': {
            'name': 'Biometric Churn',
            'description': 'High rate of biometric recapture suggesting manipulation',
            'threshold': 0.30,  # 30% recapture ratio
        },
        'CRA': {
            'name': 'Child Ratio Anomaly',
            'description': 'Unusual proportion of child enrollments',
            'threshold': 3.0,  # Z-score > 3
        },
        'CPS': {
            'name': 'Coordinated PIN Spike',
            'description': 'Simultaneous spike in enrollment, demographic, and biometric activity',
            'combined_threshold': 6.0  # Combined risk score
        },
        # NEW PATTERNS - Based on real-world Aadhaar fraud research
        'GHE': {
            'name': 'Ghost Enrollment Pattern',
            'description': 'Suspicious elderly age group activity suggesting deceased identity misuse',
            'adult_ratio_threshold': 0.95,  # >95% adult enrollments (unusual)
            'update_threshold': 5.0  # High update velocity in elderly-dominated PIN
        },
        'OPC': {
            'name': 'Operator Collusion Indicator',
            'description': 'Single PIN with extreme volumes suggesting operator fraud ring',
            'volume_percentile': 99,  # Top 1% by volume
            'combined_velocity_threshold': 8.0  # Very high combined velocity
        },
        'MPS': {
            'name': 'Multi-PIN Synchronization',
            'description': 'Multiple PINs in same district spiking simultaneously',
            'district_spike_threshold': 0.3,  # >30% of district PINs elevated
            'min_affected_pins': 5
        }
    }
    
    def __init__(self):
        """Initialize the IOCDetector."""
        self.ioc_counter = 0
        self.detected_iocs = []
    
    def _generate_ioc_id(self, pattern_code: str) -> str:
        """
        Generate unique IOC identifier.
        
        Args:
            pattern_code: IOC pattern code (MES, DMS, BIO, CRA, CPS)
            
        Returns:
            Unique IOC ID
        """
        self.ioc_counter += 1
        return f"IOC-{pattern_code}-{self.ioc_counter:06d}"
    
    def _get_recommended_action(self, risk_level: str, pattern_name: str) -> str:
        """
        Get recommended action based on risk level and pattern type.
        
        Args:
            risk_level: Risk category (CRITICAL, HIGH, MEDIUM, LOW)
            pattern_name: Name of the IOC pattern
            
        Returns:
            Recommended action string
        """
        actions = {
            'CRITICAL': {
                'Mass Enrollment Spike': 'URGENT: Suspend enrollment operations at affected centers. Escalate to Field Investigation Unit within 24 hours.',
                'Demographic Surge': 'URGENT: Freeze demographic updates. Cross-verify with source documents immediately.',
                'Biometric Churn': 'URGENT: Review biometric capture quality. Investigate operator collusion patterns.',
                'Child Ratio Anomaly': 'URGENT: Verify birth records against hospital registries. Check for ghost enrollments.',
                'Coordinated PIN Spike': 'URGENT: Full forensic audit required. Multiple indicators suggest coordinated fraud ring.'
            },
            'HIGH': {
                'Mass Enrollment Spike': 'Schedule field verification within 48 hours. Review enrollment center logs.',
                'Demographic Surge': 'Sample audit of recent demographic updates. Flag for supervisor review.',
                'Biometric Churn': 'Operator performance review. Compare biometric quality scores over time.',
                'Child Ratio Anomaly': 'Birth certificate verification for enrollments in past 30 days.',
                'Coordinated PIN Spike': 'Multi-dimensional audit within 72 hours. Cross-reference with nearby PINs.'
            },
            'MEDIUM': {
                'Mass Enrollment Spike': 'Add to weekly review queue. Monitor for escalation.',
                'Demographic Surge': 'Flag for next monthly audit cycle.',
                'Biometric Churn': 'Track operator patterns over next 30 days.',
                'Child Ratio Anomaly': 'Include in quarterly child enrollment review.',
                'Coordinated PIN Spike': 'Establish baseline. Track for potential escalation.'
            }
        }
        
        default_action = 'Continue monitoring. Log for trend analysis.'
        return actions.get(risk_level, {}).get(pattern_name, default_action)
    
    def detect_mass_enrollment_spike(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Mass Enrollment Spike pattern.
        
        Trigger: >400% increase in enrollments within 7 days
        
        Args:
            df: DataFrame with enrollment data
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['MES']
        iocs = []
        
        if 'enrollment_velocity' not in df.columns:
            return pd.DataFrame()
        
        # Threshold: velocity > 4.0 (400% of median)
        mask = df['enrollment_velocity'] > pattern['threshold']
        flagged = df[mask].copy()
        
        for idx, row in flagged.iterrows():
            ioc = {
                'ioc_id': self._generate_ioc_id('MES'),
                'pattern_code': 'MES',
                'pattern_name': pattern['name'],
                'pincode': row.get('pincode', 'N/A'),
                'district': row.get('district', 'N/A'),
                'state': row.get('state', 'N/A'),
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'first_date': str(row.get('first_date', 'N/A')),
                'last_date': str(row.get('last_date', 'N/A')),
                'risk_score': row.get('risk_score', 0),
                'risk_level': row.get('risk_level', 'UNKNOWN'),
                'indicator_value': row.get('enrollment_velocity', 0),
                'threshold': pattern['threshold'],
                'description': f"Enrollment velocity {row.get('enrollment_velocity', 0):.2f}x exceeds threshold of {pattern['threshold']}x",
                'recommended_action': self._get_recommended_action(row.get('risk_level', 'MEDIUM'), pattern['name'])
            }
            iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_demographic_surge(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Demographic Surge pattern.
        
        Trigger: >3× median demographic updates
        
        Args:
            df: DataFrame with demographic update data
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['DMS']
        iocs = []
        
        if 'update_velocity' not in df.columns:
            return pd.DataFrame()
        
        # Threshold: update velocity > 3.0 (3x median)
        mask = df['update_velocity'] > pattern['threshold']
        flagged = df[mask].copy()
        
        for idx, row in flagged.iterrows():
            ioc = {
                'ioc_id': self._generate_ioc_id('DMS'),
                'pattern_code': 'DMS',
                'pattern_name': pattern['name'],
                'pincode': row.get('pincode', 'N/A'),
                'district': row.get('district', 'N/A'),
                'state': row.get('state', 'N/A'),
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'first_date': str(row.get('first_date', 'N/A')),
                'last_date': str(row.get('last_date', 'N/A')),
                'risk_score': row.get('risk_score', 0),
                'risk_level': row.get('risk_level', 'UNKNOWN'),
                'indicator_value': row.get('update_velocity', 0),
                'threshold': pattern['threshold'],
                'description': f"Demographic update velocity {row.get('update_velocity', 0):.2f}x exceeds threshold of {pattern['threshold']}x",
                'recommended_action': self._get_recommended_action(row.get('risk_level', 'MEDIUM'), pattern['name'])
            }
            iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_biometric_churn(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Biometric Churn pattern.
        
        Trigger: >30% biometric recapture ratio
        
        Args:
            df: DataFrame with biometric data
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['BIO']
        iocs = []
        
        if 'bio_recapture_ratio' not in df.columns:
            return pd.DataFrame()
        
        # Threshold: bio recapture ratio > 0.30 (30%)
        mask = df['bio_recapture_ratio'] > pattern['threshold']
        flagged = df[mask].copy()
        
        for idx, row in flagged.iterrows():
            ioc = {
                'ioc_id': self._generate_ioc_id('BIO'),
                'pattern_code': 'BIO',
                'pattern_name': pattern['name'],
                'pincode': row.get('pincode', 'N/A'),
                'district': row.get('district', 'N/A'),
                'state': row.get('state', 'N/A'),
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'first_date': str(row.get('first_date', 'N/A')),
                'last_date': str(row.get('last_date', 'N/A')),
                'risk_score': row.get('risk_score', 0),
                'risk_level': row.get('risk_level', 'UNKNOWN'),
                'indicator_value': row.get('bio_recapture_ratio', 0),
                'threshold': pattern['threshold'],
                'description': f"Biometric recapture ratio {row.get('bio_recapture_ratio', 0):.1%} exceeds threshold of {pattern['threshold']:.0%}",
                'recommended_action': self._get_recommended_action(row.get('risk_level', 'MEDIUM'), pattern['name'])
            }
            iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_child_ratio_anomaly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Child Ratio Anomaly pattern.
        
        Trigger: Z-score > 3 for child ratio
        
        Args:
            df: DataFrame with child ratio Z-scores
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['CRA']
        iocs = []
        
        if 'child_ratio_zscore' not in df.columns:
            return pd.DataFrame()
        
        # Threshold: |Z-score| > 3
        mask = df['child_ratio_zscore'].abs() > pattern['threshold']
        flagged = df[mask].copy()
        
        for idx, row in flagged.iterrows():
            zscore = row.get('child_ratio_zscore', 0)
            direction = "abnormally high" if zscore > 0 else "abnormally low"
            
            ioc = {
                'ioc_id': self._generate_ioc_id('CRA'),
                'pattern_code': 'CRA',
                'pattern_name': pattern['name'],
                'pincode': row.get('pincode', 'N/A'),
                'district': row.get('district', 'N/A'),
                'state': row.get('state', 'N/A'),
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'first_date': str(row.get('first_date', 'N/A')),
                'last_date': str(row.get('last_date', 'N/A')),
                'risk_score': row.get('risk_score', 0),
                'risk_level': row.get('risk_level', 'UNKNOWN'),
                'indicator_value': zscore,
                'threshold': pattern['threshold'],
                'description': f"Child ratio Z-score {zscore:.2f} is {direction} (threshold: ±{pattern['threshold']})",
                'recommended_action': self._get_recommended_action(row.get('risk_level', 'MEDIUM'), pattern['name'])
            }
            iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_coordinated_spike(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Coordinated PIN Spike pattern.
        
        Trigger: High enrollment + demographic + biometric activity simultaneously
        
        Args:
            df: DataFrame with all velocity metrics
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['CPS']
        iocs = []
        
        required_cols = ['enrollment_velocity', 'update_velocity', 'bio_velocity']
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()
        
        # Calculate combined spike indicator
        # All three velocities must be elevated
        enroll_high = df['enrollment_velocity'] > 2.0
        demo_high = df['update_velocity'] > 2.0
        bio_high = df['bio_velocity'] > 2.0
        
        # Combined score for coordinated activity
        combined_velocity = (
            df['enrollment_velocity'] + 
            df['update_velocity'] + 
            df['bio_velocity']
        ) / 3
        
        mask = enroll_high & demo_high & bio_high & (combined_velocity > pattern['combined_threshold'])
        flagged = df[mask].copy()
        
        for idx, row in flagged.iterrows():
            ioc = {
                'ioc_id': self._generate_ioc_id('CPS'),
                'pattern_code': 'CPS',
                'pattern_name': pattern['name'],
                'pincode': row.get('pincode', 'N/A'),
                'district': row.get('district', 'N/A'),
                'state': row.get('state', 'N/A'),
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'first_date': str(row.get('first_date', 'N/A')),
                'last_date': str(row.get('last_date', 'N/A')),
                'risk_score': row.get('risk_score', 0),
                'risk_level': row.get('risk_level', 'UNKNOWN'),
                'indicator_value': (row.get('enrollment_velocity', 0) + row.get('update_velocity', 0) + row.get('bio_velocity', 0)) / 3,
                'threshold': pattern['combined_threshold'],
                'description': f"Coordinated spike: Enrollment {row.get('enrollment_velocity', 0):.1f}x, Demo {row.get('update_velocity', 0):.1f}x, Bio {row.get('bio_velocity', 0):.1f}x",
                'recommended_action': self._get_recommended_action(row.get('risk_level', 'MEDIUM'), pattern['name'])
            }
            iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_ghost_enrollment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Ghost Enrollment Pattern.
        
        Based on research: Fraudsters use deceased individuals' Aadhaar for benefits.
        Trigger: Abnormally high adult-only enrollment ratio + high update activity
        
        Args:
            df: DataFrame with enrollment and demographic data
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['GHE']
        iocs = []
        
        # Calculate adult ratio if possible
        if 'total_enrollment' not in df.columns:
            return pd.DataFrame()
        
        # Check for age distribution anomalies
        # If only adult enrollments and high updates, suspicious
        if 'child_ratio' in df.columns and 'update_velocity' in df.columns:
            # Very low child ratio (<5%) + high update velocity
            mask = (
                (df['child_ratio'] < 0.05) & 
                (df['update_velocity'] > pattern['update_threshold']) &
                (df['total_enrollment'] > 50)  # Minimum volume to be significant
            )
            flagged = df[mask].copy()
            
            for idx, row in flagged.iterrows():
                ioc = {
                    'ioc_id': self._generate_ioc_id('GHE'),
                    'pattern_code': 'GHE',
                    'pattern_name': pattern['name'],
                    'pincode': row.get('pincode', 'N/A'),
                    'district': row.get('district', 'N/A'),
                    'state': row.get('state', 'N/A'),
                    'date_detected': datetime.now().strftime('%Y-%m-%d'),
                    'first_date': str(row.get('first_date', 'N/A')),
                    'last_date': str(row.get('last_date', 'N/A')),
                    'risk_score': row.get('risk_score', 0),
                    'risk_level': 'HIGH',  # Ghost patterns are serious
                    'indicator_value': row.get('update_velocity', 0),
                    'threshold': pattern['update_threshold'],
                    'description': f"Ghost pattern: Child ratio {row.get('child_ratio', 0):.1%}, Update velocity {row.get('update_velocity', 0):.1f}x - possible deceased identity misuse",
                    'recommended_action': 'INVESTIGATE: Cross-reference enrollments with death registry. Verify identity documents for recent updates.'
                }
                iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_operator_collusion(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Operator Collusion Indicator.
        
        Based on research: Corrupt enrollment operators create fake/duplicate entries.
        Trigger: Single PIN with extreme combined volumes suggesting operator fraud ring
        
        Args:
            df: DataFrame with enrollment, demographic, and biometric data
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['OPC']
        iocs = []
        
        required_cols = ['enrollment_velocity', 'update_velocity', 'bio_velocity', 'total_enrollment']
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()
        
        # Combined velocity score
        df = df.copy()
        df['combined_velocity'] = (
            df['enrollment_velocity'] + 
            df['update_velocity'] + 
            df['bio_velocity']
        )
        
        # Flag top 1% by combined velocity with high absolute volume
        velocity_threshold = df['combined_velocity'].quantile(0.99)
        volume_threshold = df['total_enrollment'].quantile(0.95)
        
        mask = (
            (df['combined_velocity'] > velocity_threshold) &
            (df['combined_velocity'] > pattern['combined_velocity_threshold']) &
            (df['total_enrollment'] > volume_threshold)
        )
        flagged = df[mask].copy()
        
        for idx, row in flagged.iterrows():
            combined = row.get('combined_velocity', 0)
            ioc = {
                'ioc_id': self._generate_ioc_id('OPC'),
                'pattern_code': 'OPC',
                'pattern_name': pattern['name'],
                'pincode': row.get('pincode', 'N/A'),
                'district': row.get('district', 'N/A'),
                'state': row.get('state', 'N/A'),
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'first_date': str(row.get('first_date', 'N/A')),
                'last_date': str(row.get('last_date', 'N/A')),
                'risk_score': row.get('risk_score', 0),
                'risk_level': 'CRITICAL',  # Operator collusion is critical
                'indicator_value': combined,
                'threshold': pattern['combined_velocity_threshold'],
                'description': f"Extreme activity: Combined velocity {combined:.1f}x, Volume {row.get('total_enrollment', 0):,.0f} - investigate enrollment center operations",
                'recommended_action': 'CRITICAL: Suspend enrollment operations. Audit operator logs. Cross-verify with fingerprint quality scores.'
            }
            iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_multi_pin_sync(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Multi-PIN Synchronization pattern.
        
        Based on research: Fraud rings operate across multiple nearby PINs.
        Trigger: Multiple PINs in same district showing elevated activity
        
        Args:
            df: DataFrame with district and velocity data
            
        Returns:
            DataFrame of detected IOCs
        """
        pattern = self.IOC_PATTERNS['MPS']
        iocs = []
        
        if 'district' not in df.columns or 'enrollment_velocity' not in df.columns:
            return pd.DataFrame()
        
        # Identify elevated PINs (velocity > 2x)
        df = df.copy()
        df['is_elevated'] = df['enrollment_velocity'] > 2.0
        
        # Calculate district-level statistics
        district_stats = df.groupby('district').agg({
            'is_elevated': ['sum', 'count'],
            'state': 'first',
            'enrollment_velocity': 'mean'
        }).reset_index()
        district_stats.columns = ['district', 'elevated_count', 'total_pins', 'state', 'avg_velocity']
        
        district_stats['elevated_ratio'] = district_stats['elevated_count'] / district_stats['total_pins']
        
        # Flag districts with synchronized spikes
        sync_districts = district_stats[
            (district_stats['elevated_ratio'] > pattern['district_spike_threshold']) &
            (district_stats['elevated_count'] >= pattern['min_affected_pins'])
        ]
        
        for idx, row in sync_districts.iterrows():
            district = row['district']
            affected_pins = df[(df['district'] == district) & (df['is_elevated'])]['pincode'].tolist()
            
            ioc = {
                'ioc_id': self._generate_ioc_id('MPS'),
                'pattern_code': 'MPS',
                'pattern_name': pattern['name'],
                'pincode': ', '.join(map(str, affected_pins[:5])) + ('...' if len(affected_pins) > 5 else ''),
                'district': district,
                'state': row['state'],
                'date_detected': datetime.now().strftime('%Y-%m-%d'),
                'first_date': 'N/A',
                'last_date': 'N/A',
                'risk_score': min(10, row['avg_velocity'] * 1.5),
                'risk_level': 'HIGH',
                'indicator_value': row['elevated_ratio'],
                'threshold': pattern['district_spike_threshold'],
                'description': f"Synchronized spike across {int(row['elevated_count'])} PINs ({row['elevated_ratio']:.0%}) in district {district}",
                'recommended_action': 'INVESTIGATE: District-wide audit required. Check for common operators/centers across flagged PINs.'
            }
            iocs.append(ioc)
        
        return pd.DataFrame(iocs)
    
    def detect_all_iocs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run all IOC detection patterns.
        
        Args:
            df: DataFrame with all features and risk scores
            
        Returns:
            Combined DataFrame of all detected IOCs
        """
        print("Detecting IOCs...")
        
        all_iocs = []
        
        # Mass Enrollment Spike
        mes_iocs = self.detect_mass_enrollment_spike(df)
        if len(mes_iocs) > 0:
            all_iocs.append(mes_iocs)
            print(f"  ✓ Mass Enrollment Spike: {len(mes_iocs)} detected")
        else:
            print(f"  ✓ Mass Enrollment Spike: 0 detected")
        
        # Demographic Surge
        dms_iocs = self.detect_demographic_surge(df)
        if len(dms_iocs) > 0:
            all_iocs.append(dms_iocs)
            print(f"  ✓ Demographic Surge: {len(dms_iocs)} detected")
        else:
            print(f"  ✓ Demographic Surge: 0 detected")
        
        # Biometric Churn
        bio_iocs = self.detect_biometric_churn(df)
        if len(bio_iocs) > 0:
            all_iocs.append(bio_iocs)
            print(f"  ✓ Biometric Churn: {len(bio_iocs)} detected")
        else:
            print(f"  ✓ Biometric Churn: 0 detected")
        
        # Child Ratio Anomaly
        cra_iocs = self.detect_child_ratio_anomaly(df)
        if len(cra_iocs) > 0:
            all_iocs.append(cra_iocs)
            print(f"  ✓ Child Ratio Anomaly: {len(cra_iocs)} detected")
        else:
            print(f"  ✓ Child Ratio Anomaly: 0 detected")
        
        # Coordinated PIN Spike
        cps_iocs = self.detect_coordinated_spike(df)
        if len(cps_iocs) > 0:
            all_iocs.append(cps_iocs)
            print(f"  ✓ Coordinated PIN Spike: {len(cps_iocs)} detected")
        else:
            print(f"  ✓ Coordinated PIN Spike: 0 detected")
        
        # NEW PATTERN: Ghost Enrollment
        ghe_iocs = self.detect_ghost_enrollment(df)
        if len(ghe_iocs) > 0:
            all_iocs.append(ghe_iocs)
            print(f"  ✓ Ghost Enrollment Pattern: {len(ghe_iocs)} detected")
        else:
            print(f"  ✓ Ghost Enrollment Pattern: 0 detected")
        
        # NEW PATTERN: Operator Collusion
        opc_iocs = self.detect_operator_collusion(df)
        if len(opc_iocs) > 0:
            all_iocs.append(opc_iocs)
            print(f"  ✓ Operator Collusion Indicator: {len(opc_iocs)} detected")
        else:
            print(f"  ✓ Operator Collusion Indicator: 0 detected")
        
        # NEW PATTERN: Multi-PIN Synchronization
        mps_iocs = self.detect_multi_pin_sync(df)
        if len(mps_iocs) > 0:
            all_iocs.append(mps_iocs)
            print(f"  ✓ Multi-PIN Synchronization: {len(mps_iocs)} detected")
        else:
            print(f"  ✓ Multi-PIN Synchronization: 0 detected")
        
        if all_iocs:
            combined = pd.concat(all_iocs, ignore_index=True)
            
            # Sort by risk score descending
            combined = combined.sort_values('risk_score', ascending=False)
            
            # Store for reference
            self.detected_iocs = combined.to_dict('records')
            
            print(f"\n  Total IOCs detected: {len(combined)}")
            print(f"  By risk level:")
            for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                count = (combined['risk_level'] == level).sum()
                if count > 0:
                    print(f"    {level}: {count}")
            
            return combined
        else:
            print("\n  No IOCs detected")
            return pd.DataFrame()
    
    def get_ioc_summary(self, ioc_df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for detected IOCs.
        
        Args:
            ioc_df: DataFrame of detected IOCs
            
        Returns:
            Dictionary of summary statistics
        """
        if ioc_df.empty:
            return {
                'total_iocs': 0,
                'by_pattern': {},
                'by_risk_level': {},
                'by_state': {},
                'affected_pincodes': 0
            }
        
        summary = {
            'total_iocs': len(ioc_df),
            'by_pattern': ioc_df['pattern_name'].value_counts().to_dict(),
            'by_risk_level': ioc_df['risk_level'].value_counts().to_dict(),
            'by_state': ioc_df['state'].value_counts().head(10).to_dict(),
            'affected_pincodes': ioc_df['pincode'].nunique()
        }
        
        return summary
    
    def generate_alerts(self, ioc_df: pd.DataFrame, min_risk_level: str = 'MEDIUM') -> pd.DataFrame:
        """
        Generate actionable alerts from IOCs.
        
        Args:
            ioc_df: DataFrame of detected IOCs
            min_risk_level: Minimum risk level to include in alerts
            
        Returns:
            DataFrame of alerts
        """
        if ioc_df.empty:
            return pd.DataFrame()
        
        # Filter by risk level
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        min_order = risk_order.get(min_risk_level, 2)
        
        alerts = ioc_df[ioc_df['risk_level'].map(risk_order) <= min_order].copy()
        
        # Add alert-specific fields
        alerts['alert_id'] = ['ALERT-' + str(i+1).zfill(6) for i in range(len(alerts))]
        alerts['alert_status'] = 'OPEN'
        alerts['assigned_to'] = 'UNASSIGNED'
        alerts['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Prioritize by risk
        alerts['priority'] = alerts['risk_level'].map({
            'CRITICAL': 1,
            'HIGH': 2,
            'MEDIUM': 3,
            'LOW': 4
        })
        
        alerts = alerts.sort_values('priority')
        
        return alerts


def detect_iocs(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to detect IOCs and generate alerts.
    
    Args:
        df: DataFrame with all features and risk scores
        
    Returns:
        Tuple of (ioc_catalogue, alerts)
    """
    detector = IOCDetector()
    ioc_catalogue = detector.detect_all_iocs(df)
    alerts = detector.generate_alerts(ioc_catalogue)
    return ioc_catalogue, alerts


if __name__ == "__main__":
    # Test the module
    import os
    import sys
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    
    from cleaning import get_merged_data
    from features import engineer_features
    from risk_scoring import calculate_risk_scores
    
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    print("=" * 60)
    print("A-SOC IOC Detection Module Test")
    print("=" * 60)
    
    # Load and process data
    df = get_merged_data(data_dir, aggregation_level='pin')
    df = engineer_features(df)
    df = calculate_risk_scores(df)
    
    # Detect IOCs
    detector = IOCDetector()
    ioc_catalogue = detector.detect_all_iocs(df)
    
    print("\n" + "=" * 60)
    print("IOC Summary")
    print("=" * 60)
    
    summary = detector.get_ioc_summary(ioc_catalogue)
    print(f"\nTotal IOCs: {summary['total_iocs']}")
    print(f"Affected PIN Codes: {summary['affected_pincodes']}")
    
    print("\nBy Pattern:")
    for pattern, count in summary['by_pattern'].items():
        print(f"  {pattern}: {count}")
    
    print("\nBy Risk Level:")
    for level, count in summary['by_risk_level'].items():
        print(f"  {level}: {count}")
    
    if not ioc_catalogue.empty:
        print("\n" + "=" * 60)
        print("Sample Critical IOCs")
        print("=" * 60)
        
        critical = ioc_catalogue[ioc_catalogue['risk_level'] == 'CRITICAL'].head(5)
        if not critical.empty:
            for idx, row in critical.iterrows():
                print(f"\n{row['ioc_id']}")
                print(f"  Pattern: {row['pattern_name']}")
                print(f"  Location: {row['pincode']}, {row['district']}, {row['state']}")
                print(f"  Description: {row['description']}")
                print(f"  Action: {row['recommended_action'][:80]}...")
