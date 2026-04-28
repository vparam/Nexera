"""
Cloud Infrastructure Data Simulator
Generates realistic cloud usage and cost data for demonstration
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class CloudDataSimulator:
    """Simulates cloud infrastructure data for cost analysis"""

    def __init__(self, seed: int = 42):
        """Initialize simulator with random seed for reproducibility"""
        np.random.seed(seed)
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1',
                       'ap-southeast-1', 'ap-northeast-1', 'ca-central-1',
                       'sa-east-1', 'ap-south-1', 'us-east-2', 'eu-west-2', 'ap-southeast-2']

        self.instance_types = {
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'm5.2xlarge': 0.384,
            'c5.large': 0.085,
            'c5.xlarge': 0.170,
            'r5.large': 0.126,
            'r5.xlarge': 0.252,
            't3.medium': 0.0416,
            't3.large': 0.0832,
        }

    def generate_ec2_instances(self, count: int = 2847) -> pd.DataFrame:
        """Generate EC2 instance data"""

        instances = []
        for i in range(count):
            instance_type = np.random.choice(list(self.instance_types.keys()),
                                            p=[0.25, 0.15, 0.10, 0.15, 0.10, 0.10, 0.05, 0.05, 0.05])

            # Simulate usage patterns
            is_production = np.random.random() > 0.4
            is_critical = np.random.random() > 0.7 if is_production else False

            # Business hours usage (9AM-5PM weekdays)
            weekday_usage = np.random.uniform(0.7, 0.95) if is_production else np.random.uniform(0.3, 0.6)
            weekend_usage = np.random.uniform(0.1, 0.3) if is_production else np.random.uniform(0.05, 0.15)
            night_usage = np.random.uniform(0.4, 0.7) if is_production else np.random.uniform(0.1, 0.3)

            instances.append({
                'instance_id': f'i-{np.random.randint(1000000, 9999999):07x}',
                'instance_type': instance_type,
                'region': np.random.choice(self.regions),
                'environment': 'production' if is_production else np.random.choice(['staging', 'development', 'test']),
                'is_critical': is_critical,
                'hourly_cost': self.instance_types[instance_type],
                'weekday_utilization': weekday_usage,
                'weekend_utilization': weekend_usage,
                'night_utilization': night_usage,
                'avg_cpu_usage': np.random.uniform(0.15, 0.85),
                'avg_memory_usage': np.random.uniform(0.20, 0.90),
                'spot_compatible': not is_critical and np.random.random() > 0.3,
                'uptime_hours_per_month': 730,  # Full month
                'tags': {
                    'Team': np.random.choice(['data-science', 'backend', 'frontend', 'ml-ops', 'analytics']),
                    'Project': np.random.choice(['product-api', 'data-pipeline', 'ml-training', 'web-app', 'batch-jobs'])
                }
            })

        return pd.DataFrame(instances)

    def generate_storage_data(self, total_tb: float = 156) -> pd.DataFrame:
        """Generate storage usage data"""

        storage_items = []
        num_buckets = int(total_tb * 4)  # Average ~40GB per bucket

        for i in range(num_buckets):
            size_gb = np.random.exponential(40)  # Exponential distribution
            days_since_access = np.random.choice([
                np.random.randint(1, 30),      # 40% recent
                np.random.randint(30, 90),     # 30% medium
                np.random.randint(90, 365),    # 20% old
                np.random.randint(365, 1095)   # 10% very old
            ], p=[0.4, 0.3, 0.2, 0.1])

            storage_class = 'STANDARD'
            if days_since_access > 90:
                if np.random.random() < 0.7:
                    storage_class = 'STANDARD'  # Should be moved!
                else:
                    storage_class = 'STANDARD_IA'

            storage_items.append({
                'bucket_id': f'bucket-{i:04d}',
                'region': np.random.choice(self.regions),
                'size_gb': size_gb,
                'storage_class': storage_class,
                'days_since_last_access': days_since_access,
                'access_count_30d': max(0, int(np.random.exponential(5) if days_since_access < 30 else 0)),
                'cost_per_gb_month': 0.023 if storage_class == 'STANDARD' else 0.0125,
                'data_type': np.random.choice(['logs', 'backups', 'media', 'data-lake', 'ml-models'])
            })

        df = pd.DataFrame(storage_items)
        # Adjust to match target TB
        current_tb = df['size_gb'].sum() / 1024
        df['size_gb'] = df['size_gb'] * (total_tb / current_tb)

        return df

    def generate_cross_cloud_resources(self) -> pd.DataFrame:
        """Generate resources that exist across multiple clouds"""

        resources = []
        num_duplicates = 234

        for i in range(num_duplicates):
            resource_name = f"resource-{np.random.choice(['api', 'db', 'cache', 'lb', 'pipeline'])}-{i:03d}"

            # Duplicate across clouds
            for cloud in np.random.choice(['aws', 'gcp', 'azure'], size=2, replace=False):
                resources.append({
                    'resource_name': resource_name,
                    'cloud_provider': cloud,
                    'resource_type': np.random.choice(['load_balancer', 'database', 'cache', 'pipeline', 'monitoring']),
                    'monthly_cost': np.random.uniform(500, 5000),
                    'is_duplicate': True,
                    'team': np.random.choice(['data-science', 'backend', 'frontend', 'ml-ops']),
                    'region': np.random.choice(self.regions[:6]),
                })

        # Add some unique resources
        for i in range(100):
            resources.append({
                'resource_name': f"unique-resource-{i:03d}",
                'cloud_provider': np.random.choice(['aws', 'gcp', 'azure']),
                'resource_type': np.random.choice(['compute', 'storage', 'network']),
                'monthly_cost': np.random.uniform(100, 2000),
                'is_duplicate': False,
                'team': np.random.choice(['data-science', 'backend', 'frontend']),
                'region': np.random.choice(self.regions[:6]),
            })

        return pd.DataFrame(resources)

    def generate_ml_models(self) -> pd.DataFrame:
        """Generate ML model registry data"""

        models = []
        model_names = [f'model-{letter}' for letter in 'abcdefghij']

        for model_name in model_names:
            # Each model has many versions
            num_versions = np.random.randint(80, 150)

            for version in range(num_versions):
                days_old = version * 7 + np.random.randint(0, 7)
                size_gb = np.random.uniform(0.5, 15)

                is_active = version >= (num_versions - 3)  # Last 3 versions are active

                models.append({
                    'model_name': model_name,
                    'version': f'v{version:03d}',
                    'size_gb': size_gb,
                    'days_old': days_old,
                    'is_active': is_active,
                    'storage_cost_per_month': size_gb * 0.023 * 1.5,  # S3 + metadata overhead
                    'framework': np.random.choice(['tensorflow', 'pytorch', 'sklearn', 'xgboost']),
                    'last_accessed': datetime.now() - timedelta(days=days_old),
                    'deployment_count': np.random.randint(0, 5) if is_active else 0
                })

        return pd.DataFrame(models)

    def generate_time_series_usage(self, days: int = 30) -> pd.DataFrame:
        """Generate time series usage data for visualization"""

        dates = pd.date_range(end=datetime.now(), periods=days*24, freq='h')

        usage_data = []
        for dt in dates:
            # Simulate daily patterns
            hour = dt.hour
            is_weekend = dt.weekday() >= 5

            # Business hours pattern
            if 9 <= hour <= 17 and not is_weekend:
                base_usage = 0.75
            elif is_weekend:
                base_usage = 0.15
            else:
                base_usage = 0.35

            # Add some noise
            usage = base_usage + np.random.normal(0, 0.1)
            usage = max(0.05, min(0.95, usage))

            usage_data.append({
                'timestamp': dt,
                'cpu_utilization': usage * 100,
                'instance_count': int(2847 * usage),
                'estimated_cost_per_hour': 2847 * 0.15 * usage,  # Avg instance cost
            })

        return pd.DataFrame(usage_data)

    def generate_complete_dataset(self) -> Dict[str, pd.DataFrame]:
        """Generate complete dataset for demo"""

        return {
            'ec2_instances': self.generate_ec2_instances(),
            'storage': self.generate_storage_data(),
            'cross_cloud': self.generate_cross_cloud_resources(),
            'ml_models': self.generate_ml_models(),
            'time_series': self.generate_time_series_usage()
        }


if __name__ == '__main__':
    # Test the simulator
    simulator = CloudDataSimulator()
    data = simulator.generate_complete_dataset()

    print("Generated Data Summary:")
    print("=" * 50)
    for name, df in data.items():
        print(f"\n{name}:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)[:5]}...")
        if 'monthly_cost' in df.columns:
            print(f"  Total Monthly Cost: ${df['monthly_cost'].sum():,.2f}")
