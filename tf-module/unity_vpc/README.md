# VPC Terraform Module

This Terraform configuration recreates a VPC based on the exported configuration from an existing AWS account.

## Architecture

The VPC includes:

- **VPC**: Primary CIDR block (10.52.8.0/22) and secondary CIDR block (10.0.0.0/16)
- **Internet Gateway**: For public internet access
- **NAT Gateway**: Single NAT Gateway for private subnet internet access
- **Subnets**:
  - 1 NAT Gateway subnet (10.52.11.0/28)
  - 4 Public subnets across 4 availability zones
  - 4 Private subnets across 4 availability zones
- **Route Tables**: Separate route tables for public and private subnets
- **VPC Endpoints**:
  - S3 Gateway endpoint (always created)
  - Execute API interface endpoint (optional)
  - EFS interface endpoint (optional)

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Appropriate AWS permissions to create VPC resources

## Usage

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your desired configuration

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Review the plan:
   ```bash
   terraform plan
   ```

5. Apply the configuration:
   ```bash
   terraform apply
   ```

## Variables

| Name | Description | Type | Default |
|------|-------------|------|---------|
| aws_region | AWS region | string | us-west-2 |
| name_prefix | Prefix for resource names | string | Unity-VPC |
| vpc_cidr_block | Primary VPC CIDR | string | 10.52.8.0/22 |
| secondary_cidr_block | Secondary VPC CIDR | string | 10.0.0.0/16 |
| availability_zones | List of AZs | list(string) | ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"] |
| public_subnet_cidrs | Public subnet CIDRs | list(string) | See variables.tf |
| private_subnet_cidrs | Private subnet CIDRs | list(string) | See variables.tf |
| enable_interface_endpoints | Enable VPC interface endpoints | bool | false |
| common_tags | Tags for all resources | map(string) | {Project = "Unity"} |

## Outputs

The module exports various outputs including VPC ID, subnet IDs, route table IDs, and VPC endpoint IDs. See `outputs.tf` for the complete list.

## Customization

To use different CIDR ranges or availability zones for a different AWS account:

1. Modify the `vpc_cidr_block` and `secondary_cidr_block` if needed
2. Update `availability_zones` to match your target region
3. Adjust subnet CIDRs in `public_subnet_cidrs` and `private_subnet_cidrs`
4. Update `aws_region` to your target region
5. Add or modify tags in `common_tags`

## Cost Considerations

- **NAT Gateway**: Charges per hour and per GB of data processed
- **VPC Endpoints**: Interface endpoints charge per hour and per GB processed
- **Elastic IP**: No charge when associated with a running resource

To reduce costs:
- Set `enable_interface_endpoints = false` if not needed
- Consider using a single availability zone for testing

## Notes

- Security groups are not included in this base configuration and should be created separately
- VPC peering connections from the original configuration are not included
- Some managed VPC endpoints (e.g., RabbitMQ, OpenSearch) are not included as they are service-specific
