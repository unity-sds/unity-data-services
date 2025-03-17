Setup:
- ALB (Application w/ correct security) -> 
    - Listener (on port Http, 8005) -> 
        - Target Group (Instance) -> 
            - EC2 (on port 8005 w/ correct security group)
