"""
Savings Calculator Engine
Analyzes cloud infrastructure data and calculates savings opportunities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SavingsOpportunity:
    """Represents a cost savings opportunity"""
    name: str
    monthly_savings: float
    annual_savings: float
    implementation_time: str
    risk_level: str
    confidence: float
    affected_resources: int
    description: str
    details: Dict


class SavingsCalculator:
    """Calculates savings opportunities from infrastructure data"""

    def __init__(self, data: Dict[str, pd.DataFrame]):
        """Initialize calculator with infrastructure data"""
        self.data = data
        self.opportunities = []

    def calculate_spot_instance_savings(self) -> SavingsOpportunity:
        """Calculate savings from migrating to spot instances"""

        ec2_df = self.data['ec2_instances']

        # Find spot-compatible instances
        spot_candidates = ec2_df[ec2_df['spot_compatible'] == True].copy()

        # Calculate current costs
        spot_candidates['monthly_cost'] = (
            spot_candidates['hourly_cost'] *
            spot_candidates['uptime_hours_per_month']
        )

        current_monthly_cost = spot_candidates['monthly_cost'].sum()

        # Spot instances are typically 60-90% cheaper
        # We'll use 68% savings (conservative)
        spot_discount = 0.68
        projected_spot_cost = current_monthly_cost * (1 - spot_discount)
        monthly_savings = current_monthly_cost - projected_spot_cost

        # Calculate confidence based on workload types
        non_critical = (spot_candidates['is_critical'] == False).sum()
        confidence = min(0.98, 0.85 + (non_critical / len(spot_candidates)) * 0.15)

        # Extract team info from tags
        spot_candidates['team'] = spot_candidates['tags'].apply(lambda x: x.get('Team', 'Unknown'))
        spot_candidates['project'] = spot_candidates['tags'].apply(lambda x: x.get('Project', 'Unknown'))

        details = {
            'current_monthly_cost': current_monthly_cost,
            'projected_monthly_cost': projected_spot_cost,
            'spot_discount_pct': spot_discount * 100,
            'instances_to_migrate': len(spot_candidates),
            'by_environment': spot_candidates.groupby('environment').size().to_dict(),
            'by_region': spot_candidates.groupby('region')['monthly_cost'].sum().to_dict(),
            'by_team': spot_candidates.groupby('team')['monthly_cost'].sum().to_dict(),
            'by_project': spot_candidates.groupby('project')['monthly_cost'].sum().to_dict(),
            'by_instance_type': spot_candidates.groupby('instance_type')['monthly_cost'].sum().to_dict(),
            'avg_cpu_usage': spot_candidates['avg_cpu_usage'].mean() * 100,
            'avg_memory_usage': spot_candidates['avg_memory_usage'].mean() * 100,
        }

        return SavingsOpportunity(
            name="Spot Instance Migration",
            monthly_savings=monthly_savings,
            annual_savings=monthly_savings * 12,
            implementation_time="2 hours",
            risk_level="Low",
            confidence=confidence,
            affected_resources=len(spot_candidates),
            description="Migrate non-critical workloads to spot instances with automatic fallback",
            details=details
        )

    def calculate_storage_lifecycle_savings(self) -> SavingsOpportunity:
        """Calculate savings from implementing storage lifecycle policies"""

        storage_df = self.data['storage']

        # Find data that should be in cheaper storage tiers
        # Data not accessed in 90+ days should be in Infrequent Access
        old_data = storage_df[
            (storage_df['days_since_last_access'] > 90) &
            (storage_df['storage_class'] == 'STANDARD')
        ].copy()

        # Calculate current costs
        current_monthly_cost = (old_data['size_gb'] * old_data['cost_per_gb_month']).sum()

        # Standard IA is about 45% cheaper than Standard
        ia_cost_per_gb = 0.0125
        projected_monthly_cost = old_data['size_gb'].sum() * ia_cost_per_gb
        monthly_savings = current_monthly_cost - projected_monthly_cost

        # Very high confidence - this is a cloud provider feature
        confidence = 0.99

        details = {
            'current_monthly_cost': current_monthly_cost,
            'projected_monthly_cost': projected_monthly_cost,
            'data_to_migrate_gb': old_data['size_gb'].sum(),
            'data_to_migrate_tb': old_data['size_gb'].sum() / 1024,
            'buckets_affected': len(old_data),
            'avg_days_since_access': old_data['days_since_last_access'].mean(),
            'by_data_type': old_data.groupby('data_type')['size_gb'].sum().to_dict(),
        }

        return SavingsOpportunity(
            name="Storage Lifecycle Policies",
            monthly_savings=monthly_savings,
            annual_savings=monthly_savings * 12,
            implementation_time="1 day",
            risk_level="None",
            confidence=confidence,
            affected_resources=len(old_data),
            description="Implement intelligent tiering for infrequently accessed data",
            details=details
        )

    def calculate_cross_cloud_dedup_savings(self) -> SavingsOpportunity:
        """Calculate savings from eliminating duplicate resources"""

        cross_cloud_df = self.data['cross_cloud']

        # Find duplicates
        duplicates = cross_cloud_df[cross_cloud_df['is_duplicate'] == True].copy()

        # Group by resource name to find duplicates
        duplicate_groups = duplicates.groupby('resource_name')

        # Calculate savings by keeping only one instance per resource
        total_cost = duplicates['monthly_cost'].sum()

        # Keep the cheaper instance in each group
        savings_list = []
        for resource_name, group in duplicate_groups:
            if len(group) > 1:
                # Sort by cost and remove all but the cheapest
                sorted_group = group.sort_values('monthly_cost')
                savings_list.append(sorted_group.iloc[1:]['monthly_cost'].sum())

        monthly_savings = sum(savings_list)

        # Medium-high confidence
        confidence = 0.94

        # Calculate team-specific waste
        team_waste = {}
        for team in duplicates['team'].unique():
            team_dupes = duplicates[duplicates['team'] == team]
            team_waste[team] = team_dupes['monthly_cost'].sum() / 2

        # Calculate resource type waste
        resource_type_waste = {}
        for rtype in duplicates['resource_type'].unique():
            rtype_dupes = duplicates[duplicates['resource_type'] == rtype]
            resource_type_waste[rtype] = rtype_dupes['monthly_cost'].sum() / 2

        # Calculate cloud provider combinations
        cloud_combos = duplicates.groupby('resource_name')['cloud_provider'].apply(
            lambda x: ' + '.join(sorted(x.unique()))
        ).value_counts().to_dict()

        details = {
            'total_duplicate_cost': total_cost,
            'duplicate_resources': len(duplicate_groups),
            'duplicate_instances': len(duplicates),
            'by_cloud': duplicates.groupby('cloud_provider')['monthly_cost'].sum().to_dict(),
            'by_resource_type': duplicates.groupby('resource_type')['monthly_cost'].sum().to_dict(),
            'by_team': duplicates.groupby('team')['monthly_cost'].sum().to_dict(),
            'team_waste': team_waste,
            'resource_type_waste': resource_type_waste,
            'cloud_combinations': cloud_combos,
            'by_region': duplicates.groupby('region')['monthly_cost'].sum().to_dict(),
        }

        return SavingsOpportunity(
            name="Cross-Cloud Deduplication",
            monthly_savings=monthly_savings,
            annual_savings=monthly_savings * 12,
            implementation_time="1 week",
            risk_level="Low",
            confidence=confidence,
            affected_resources=len(duplicate_groups),
            description="Eliminate duplicate resources across AWS, Azure, and GCP",
            details=details
        )

    def calculate_ml_model_registry_savings(self) -> SavingsOpportunity:
        """Calculate savings from optimizing ML model storage"""

        models_df = self.data['ml_models']

        # Find inactive old versions that can be pruned
        # Keep active models + last 30 days of inactive as buffer
        prunable = models_df[
            (models_df['is_active'] == False) &
            (models_df['days_old'] > 90)
        ].copy()

        # Calculate savings
        monthly_savings = prunable['storage_cost_per_month'].sum()

        # Medium confidence due to potential need for old models
        confidence = 0.87

        # Calculate retention policy impact
        total_models = len(models_df)
        total_versions = models_df.groupby('model_name').size().mean()

        details = {
            'current_monthly_cost': models_df['storage_cost_per_month'].sum(),
            'projected_monthly_cost': models_df['storage_cost_per_month'].sum() - monthly_savings,
            'models_to_prune': len(prunable),
            'total_models': total_models,
            'avg_versions_per_model': total_versions,
            'storage_freed_gb': prunable['size_gb'].sum(),
            'storage_freed_tb': prunable['size_gb'].sum() / 1024,
            'by_framework': prunable.groupby('framework')['storage_cost_per_month'].sum().to_dict(),
        }

        return SavingsOpportunity(
            name="Model Registry Optimization",
            monthly_savings=monthly_savings,
            annual_savings=monthly_savings * 12,
            implementation_time="2 weeks",
            risk_level="Medium",
            confidence=confidence,
            affected_resources=len(prunable),
            description="Consolidate ML model storage and implement version pruning",
            details=details
        )

    def calculate_all_opportunities(self) -> List[SavingsOpportunity]:
        """Calculate all savings opportunities"""

        self.opportunities = [
            self.calculate_spot_instance_savings(),
            self.calculate_storage_lifecycle_savings(),
            self.calculate_cross_cloud_dedup_savings(),
            self.calculate_ml_model_registry_savings(),
        ]

        # Sort by monthly savings (descending)
        self.opportunities.sort(key=lambda x: x.monthly_savings, reverse=True)

        return self.opportunities

    def get_summary_metrics(self) -> Dict:
        """Get summary metrics for all opportunities"""

        if not self.opportunities:
            self.calculate_all_opportunities()

        total_monthly = sum(opp.monthly_savings for opp in self.opportunities)
        total_annual = sum(opp.annual_savings for opp in self.opportunities)

        # Calculate top 3 quick wins (low/no risk, fast implementation)
        quick_wins = [opp for opp in self.opportunities
                     if opp.risk_level in ['None', 'Low']][:3]
        quick_win_monthly = sum(opp.monthly_savings for opp in quick_wins)

        # Calculate infrastructure stats
        ec2_df = self.data['ec2_instances']
        storage_df = self.data['storage']

        return {
            'total_monthly_savings': total_monthly,
            'total_annual_savings': total_annual,
            'quick_win_monthly': quick_win_monthly,
            'quick_win_annual': quick_win_monthly * 12,
            'total_opportunities': len(self.opportunities),
            'infrastructure': {
                'ec2_instances': len(ec2_df),
                'regions': ec2_df['region'].nunique(),
                'storage_tb': storage_df['size_gb'].sum() / 1024,
                'avg_cpu_utilization': ec2_df['avg_cpu_usage'].mean() * 100,
                'weekend_utilization': ec2_df['weekend_utilization'].mean() * 100,
            }
        }

    def calculate_roi(self, investment: float = 5.4) -> Dict:
        """Calculate ROI metrics"""

        summary = self.get_summary_metrics()
        annual_savings = summary['total_annual_savings']
        monthly_savings = summary['total_monthly_savings']

        # Payback period in months
        payback_months = investment / monthly_savings

        # 3-year NPV at 10% discount rate
        discount_rate = 0.10
        npv = -investment
        for year in range(1, 4):
            npv += annual_savings / ((1 + discount_rate) ** year)

        # First year ROI
        roi_pct = ((annual_savings - investment) / investment) * 100

        return {
            'investment_millions': investment,
            'payback_months': payback_months,
            'payback_days': payback_months * 30,
            'first_year_roi_pct': roi_pct,
            'npv_3_year': npv,
            'annual_savings': annual_savings,
            'monthly_savings': monthly_savings,
        }


if __name__ == '__main__':
    # Test the calculator
    from data_simulator import CloudDataSimulator

    print("Generating simulated data...")
    simulator = CloudDataSimulator()
    data = simulator.generate_complete_dataset()

    print("\nCalculating savings opportunities...")
    calculator = SavingsCalculator(data)
    opportunities = calculator.calculate_all_opportunities()

    print("\n" + "=" * 60)
    print("SAVINGS OPPORTUNITIES")
    print("=" * 60)

    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp.name}")
        print(f"   Monthly Savings: ${opp.monthly_savings / 1_000_000:.1f}M")
        print(f"   Annual Savings: ${opp.annual_savings / 1_000_000:.1f}M")
        print(f"   Implementation: {opp.implementation_time}")
        print(f"   Risk: {opp.risk_level}")
        print(f"   Confidence: {opp.confidence * 100:.0f}%")
        print(f"   Affected Resources: {opp.affected_resources}")

    print("\n" + "=" * 60)
    summary = calculator.get_summary_metrics()
    print(f"Total Monthly Savings: ${summary['total_monthly_savings'] / 1_000_000:.1f}M")
    print(f"Total Annual Savings: ${summary['total_annual_savings'] / 1_000_000:.1f}M")
    print(f"Week 1 Quick Wins: ${summary['quick_win_monthly'] / 1_000_000:.1f}M/month")

    print("\n" + "=" * 60)
    roi = calculator.calculate_roi()
    print(f"Payback Period: {roi['payback_days']:.0f} days")
    print(f"First Year ROI: {roi['first_year_roi_pct']:.0f}%")
    print(f"3-Year NPV: ${roi['npv_3_year']:.1f}M")
