"""
A-SOC Data Cleaning Module
===========================
Handles loading, cleaning, and preprocessing of Aadhaar datasets.
Follows strict schema definitions from claude.md specification.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import glob
import warnings

warnings.filterwarnings('ignore')

# Fixed random seed for reproducibility
np.random.seed(42)


class DataCleaner:
    """
    Cleans and preprocesses Aadhaar enrollment, demographic, and biometric data.
    All processing follows the strict schema defined in claude.md.
    """
    
    # Standard column mappings from actual CSV to spec
    ENROLLMENT_COLUMNS = {
        'date': 'date',
        'state': 'state',
        'district': 'district',
        'pincode': 'pincode',
        'age_0_5': 'age_0_5',
        'age_5_17': 'age_5_17',
        'age_18_greater': 'age_18_greater'
    }
    
    DEMOGRAPHIC_COLUMNS = {
        'date': 'date',
        'state': 'state',
        'district': 'district',
        'pincode': 'pincode',
        'demo_age_5_17': 'demo_age_5_17',
        'demo_age_17_': 'demo_age_18_greater',  # Handle truncated column name
        'demo_age_18_greater': 'demo_age_18_greater'
    }
    
    BIOMETRIC_COLUMNS = {
        'date': 'date',
        'state': 'state',
        'district': 'district',
        'pincode': 'pincode',
        'bio_age_5_17': 'bio_age_5_17',
        'bio_age_17_': 'bio_age_18_greater',  # Handle truncated column name
        'bio_age_18_greater': 'bio_age_18_greater'
    }
    
    def __init__(self, data_dir: str):
        """
        Initialize the DataCleaner.
        
        Args:
            data_dir: Path to the data directory
        """
        self.data_dir = Path(data_dir)
        self.enrollment_dir = self.data_dir / 'api_data_aadhar_enrolment'
        self.demographic_dir = self.data_dir / 'api_data_aadhar_demographic'
        self.biometric_dir = self.data_dir / 'api_data_aadhar_biometric'
    
    def _load_chunked_csv(self, directory: Path, pattern: str = '*.csv') -> pd.DataFrame:
        """
        Load and concatenate multiple CSV files from a directory.
        
        Args:
            directory: Path to directory containing CSV files
            pattern: Glob pattern for CSV files
            
        Returns:
            Concatenated DataFrame
        """
        csv_files = sorted(glob.glob(str(directory / pattern)))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {directory}")
        
        dfs = []
        for file in csv_files:
            df = pd.read_csv(file, dtype=str)  # Load as string first for uniform processing
            dfs.append(df)
        
        combined = pd.concat(dfs, ignore_index=True)
        return combined
    
    def _standardize_columns(self, df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
        """
        Standardize column names according to mapping.
        
        Args:
            df: Input DataFrame
            column_mapping: Dictionary of source -> target column names
            
        Returns:
            DataFrame with standardized column names
        """
        # Convert all column names to lowercase for matching
        df.columns = df.columns.str.lower().str.strip()
        
        # Rename columns according to mapping
        rename_dict = {}
        for source, target in column_mapping.items():
            if source in df.columns:
                rename_dict[source] = target
        
        df = df.rename(columns=rename_dict)
        return df
    
    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse date column to datetime format.
        
        Args:
            df: DataFrame with 'date' column
            
        Returns:
            DataFrame with parsed dates
        """
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            # Drop rows with invalid dates
            initial_count = len(df)
            df = df.dropna(subset=['date'])
            dropped = initial_count - len(df)
            if dropped > 0:
                print(f"  Dropped {dropped} rows with invalid dates")
        return df
    
    def _convert_numeric_columns(self, df: pd.DataFrame, numeric_cols: list) -> pd.DataFrame:
        """
        Convert specified columns to numeric, filling missing with 0.
        
        Args:
            df: Input DataFrame
            numeric_cols: List of columns to convert
            
        Returns:
            DataFrame with numeric columns
        """
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df
    
    def _clean_string_columns(self, df: pd.DataFrame, string_cols: list) -> pd.DataFrame:
        """
        Clean and standardize string columns.
        
        Args:
            df: Input DataFrame
            string_cols: List of string columns to clean
            
        Returns:
            DataFrame with cleaned string columns
        """
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()
                # Replace common variations
                df[col] = df[col].replace({
                    'Andaman And Nicobar Islands': 'Andaman And Nicobar',
                    'Dadra And Nagar Haveli And Daman And Diu': 'Dadra And Nagar Haveli',
                    'Jammu And Kashmir': 'Jammu And Kashmir',
                })
        return df
    
    def _validate_pincode(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean pincode column.
        
        Args:
            df: DataFrame with pincode column
            
        Returns:
            DataFrame with validated pincodes
        """
        if 'pincode' in df.columns:
            # Convert to string, pad with zeros if needed
            df['pincode'] = df['pincode'].astype(str).str.strip()
            df['pincode'] = df['pincode'].str.replace(r'\.0$', '', regex=True)
            df['pincode'] = df['pincode'].str.zfill(6)
            
            # Remove invalid pincodes (not 6 digits)
            valid_mask = df['pincode'].str.match(r'^\d{6}$')
            invalid_count = (~valid_mask).sum()
            if invalid_count > 0:
                print(f"  Removed {invalid_count} rows with invalid pincodes")
            df = df[valid_mask].copy()
        
        return df
    
    def load_enrollment_data(self) -> pd.DataFrame:
        """
        Load and clean enrollment dataset.
        
        Returns:
            Cleaned enrollment DataFrame
        """
        print("Loading enrollment data...")
        df = self._load_chunked_csv(self.enrollment_dir)
        print(f"  Loaded {len(df):,} raw records")
        
        # Standardize columns
        df = self._standardize_columns(df, self.ENROLLMENT_COLUMNS)
        
        # Parse dates
        df = self._parse_dates(df)
        
        # Clean string columns
        df = self._clean_string_columns(df, ['state', 'district'])
        
        # Validate pincodes
        df = self._validate_pincode(df)
        
        # Convert numeric columns
        numeric_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        df = self._convert_numeric_columns(df, numeric_cols)
        
        # Calculate total enrollments
        df['total_enrollments'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
        
        print(f"  Final: {len(df):,} clean records")
        return df
    
    def load_demographic_data(self) -> pd.DataFrame:
        """
        Load and clean demographic updates dataset.
        
        Returns:
            Cleaned demographic DataFrame
        """
        print("Loading demographic data...")
        df = self._load_chunked_csv(self.demographic_dir)
        print(f"  Loaded {len(df):,} raw records")
        
        # Standardize columns
        df = self._standardize_columns(df, self.DEMOGRAPHIC_COLUMNS)
        
        # Parse dates
        df = self._parse_dates(df)
        
        # Clean string columns
        df = self._clean_string_columns(df, ['state', 'district'])
        
        # Validate pincodes
        df = self._validate_pincode(df)
        
        # Convert numeric columns
        numeric_cols = ['demo_age_5_17', 'demo_age_18_greater']
        df = self._convert_numeric_columns(df, numeric_cols)
        
        # Calculate total demographic updates
        df['total_demo_updates'] = df['demo_age_5_17'] + df['demo_age_18_greater']
        
        print(f"  Final: {len(df):,} clean records")
        return df
    
    def load_biometric_data(self) -> pd.DataFrame:
        """
        Load and clean biometric updates dataset.
        
        Returns:
            Cleaned biometric DataFrame
        """
        print("Loading biometric data...")
        df = self._load_chunked_csv(self.biometric_dir)
        print(f"  Loaded {len(df):,} raw records")
        
        # Standardize columns
        df = self._standardize_columns(df, self.BIOMETRIC_COLUMNS)
        
        # Parse dates
        df = self._parse_dates(df)
        
        # Clean string columns
        df = self._clean_string_columns(df, ['state', 'district'])
        
        # Validate pincodes
        df = self._validate_pincode(df)
        
        # Convert numeric columns
        numeric_cols = ['bio_age_5_17', 'bio_age_18_greater']
        df = self._convert_numeric_columns(df, numeric_cols)
        
        # Calculate total biometric updates
        df['total_bio_updates'] = df['bio_age_5_17'] + df['bio_age_18_greater']
        
        print(f"  Final: {len(df):,} clean records")
        return df
    
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load all three datasets.
        
        Returns:
            Tuple of (enrollment_df, demographic_df, biometric_df)
        """
        enrollment_df = self.load_enrollment_data()
        demographic_df = self.load_demographic_data()
        biometric_df = self.load_biometric_data()
        
        return enrollment_df, demographic_df, biometric_df
    
    def merge_datasets(self, 
                       enrollment_df: pd.DataFrame,
                       demographic_df: pd.DataFrame,
                       biometric_df: pd.DataFrame,
                       aggregation_level: str = 'pin_date') -> pd.DataFrame:
        """
        Merge all three datasets at specified aggregation level.
        
        Args:
            enrollment_df: Cleaned enrollment data
            demographic_df: Cleaned demographic data
            biometric_df: Cleaned biometric data
            aggregation_level: 'pin_date', 'pin', 'district', or 'state'
            
        Returns:
            Merged and aggregated DataFrame
        """
        print(f"\nMerging datasets at {aggregation_level} level...")
        
        if aggregation_level == 'pin_date':
            # Aggregate by PIN + Date
            group_cols = ['date', 'state', 'district', 'pincode']
            
            enroll_agg = enrollment_df.groupby(group_cols).agg({
                'age_0_5': 'sum',
                'age_5_17': 'sum',
                'age_18_greater': 'sum',
                'total_enrollments': 'sum'
            }).reset_index()
            
            demo_agg = demographic_df.groupby(group_cols).agg({
                'demo_age_5_17': 'sum',
                'demo_age_18_greater': 'sum',
                'total_demo_updates': 'sum'
            }).reset_index()
            
            bio_agg = biometric_df.groupby(group_cols).agg({
                'bio_age_5_17': 'sum',
                'bio_age_18_greater': 'sum',
                'total_bio_updates': 'sum'
            }).reset_index()
            
            # Merge datasets
            merged = enroll_agg.merge(demo_agg, on=group_cols, how='outer')
            merged = merged.merge(bio_agg, on=group_cols, how='outer')
            
        elif aggregation_level == 'pin':
            # Aggregate by PIN only
            group_cols = ['state', 'district', 'pincode']
            
            enroll_agg = enrollment_df.groupby(group_cols).agg({
                'age_0_5': 'sum',
                'age_5_17': 'sum',
                'age_18_greater': 'sum',
                'total_enrollments': 'sum',
                'date': ['min', 'max']
            }).reset_index()
            enroll_agg.columns = ['state', 'district', 'pincode', 'age_0_5', 'age_5_17', 
                                  'age_18_greater', 'total_enrollments', 'first_date', 'last_date']
            
            demo_agg = demographic_df.groupby(group_cols).agg({
                'demo_age_5_17': 'sum',
                'demo_age_18_greater': 'sum',
                'total_demo_updates': 'sum'
            }).reset_index()
            
            bio_agg = biometric_df.groupby(group_cols).agg({
                'bio_age_5_17': 'sum',
                'bio_age_18_greater': 'sum',
                'total_bio_updates': 'sum'
            }).reset_index()
            
            # Merge datasets
            merged = enroll_agg.merge(demo_agg, on=group_cols, how='outer')
            merged = merged.merge(bio_agg, on=group_cols, how='outer')
            
        elif aggregation_level == 'district':
            # Aggregate by District
            group_cols = ['state', 'district']
            
            enroll_agg = enrollment_df.groupby(group_cols).agg({
                'age_0_5': 'sum',
                'age_5_17': 'sum',
                'age_18_greater': 'sum',
                'total_enrollments': 'sum',
                'pincode': 'nunique'
            }).reset_index()
            enroll_agg = enroll_agg.rename(columns={'pincode': 'pin_count'})
            
            demo_agg = demographic_df.groupby(group_cols).agg({
                'demo_age_5_17': 'sum',
                'demo_age_18_greater': 'sum',
                'total_demo_updates': 'sum'
            }).reset_index()
            
            bio_agg = biometric_df.groupby(group_cols).agg({
                'bio_age_5_17': 'sum',
                'bio_age_18_greater': 'sum',
                'total_bio_updates': 'sum'
            }).reset_index()
            
            merged = enroll_agg.merge(demo_agg, on=group_cols, how='outer')
            merged = merged.merge(bio_agg, on=group_cols, how='outer')
            
        else:  # state level
            # Aggregate by State
            group_cols = ['state']
            
            enroll_agg = enrollment_df.groupby(group_cols).agg({
                'age_0_5': 'sum',
                'age_5_17': 'sum',
                'age_18_greater': 'sum',
                'total_enrollments': 'sum',
                'pincode': 'nunique',
                'district': 'nunique'
            }).reset_index()
            enroll_agg = enroll_agg.rename(columns={'pincode': 'pin_count', 'district': 'district_count'})
            
            demo_agg = demographic_df.groupby(group_cols).agg({
                'demo_age_5_17': 'sum',
                'demo_age_18_greater': 'sum',
                'total_demo_updates': 'sum'
            }).reset_index()
            
            bio_agg = biometric_df.groupby(group_cols).agg({
                'bio_age_5_17': 'sum',
                'bio_age_18_greater': 'sum',
                'total_bio_updates': 'sum'
            }).reset_index()
            
            merged = enroll_agg.merge(demo_agg, on=group_cols, how='outer')
            merged = merged.merge(bio_agg, on=group_cols, how='outer')
        
        # Fill NaN values with 0
        numeric_columns = merged.select_dtypes(include=[np.number]).columns
        merged[numeric_columns] = merged[numeric_columns].fillna(0).astype(int)
        
        print(f"  Merged dataset: {len(merged):,} records")
        return merged


def load_and_clean_data(data_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to load and clean all datasets.
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        Tuple of (enrollment_df, demographic_df, biometric_df)
    """
    cleaner = DataCleaner(data_dir)
    return cleaner.load_all_data()


def get_merged_data(data_dir: str, aggregation_level: str = 'pin') -> pd.DataFrame:
    """
    Convenience function to get merged data at specified aggregation level.
    
    Args:
        data_dir: Path to data directory
        aggregation_level: 'pin_date', 'pin', 'district', or 'state'
        
    Returns:
        Merged DataFrame
    """
    cleaner = DataCleaner(data_dir)
    enrollment_df, demographic_df, biometric_df = cleaner.load_all_data()
    return cleaner.merge_datasets(enrollment_df, demographic_df, biometric_df, aggregation_level)


if __name__ == "__main__":
    # Test the module
    import os
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    print("=" * 60)
    print("A-SOC Data Cleaning Module Test")
    print("=" * 60)
    
    cleaner = DataCleaner(data_dir)
    enrollment_df, demographic_df, biometric_df = cleaner.load_all_data()
    
    print("\n" + "=" * 60)
    print("Dataset Summaries")
    print("=" * 60)
    
    print(f"\nEnrollment Data Shape: {enrollment_df.shape}")
    print(f"Date Range: {enrollment_df['date'].min()} to {enrollment_df['date'].max()}")
    print(f"States: {enrollment_df['state'].nunique()}")
    print(f"Districts: {enrollment_df['district'].nunique()}")
    print(f"PIN Codes: {enrollment_df['pincode'].nunique()}")
    
    print(f"\nDemographic Data Shape: {demographic_df.shape}")
    print(f"Date Range: {demographic_df['date'].min()} to {demographic_df['date'].max()}")
    
    print(f"\nBiometric Data Shape: {biometric_df.shape}")
    print(f"Date Range: {biometric_df['date'].min()} to {biometric_df['date'].max()}")
    
    # Test merging
    merged = cleaner.merge_datasets(enrollment_df, demographic_df, biometric_df, 'pin')
    print(f"\nMerged PIN-level Data Shape: {merged.shape}")
