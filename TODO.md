### Future tasks


1. Update Terraform policies to accept multiple DAACs
2. Create Terraform or script to update S3 bucket policy for DAACs to accept files
3. Add additional endpoint to return all statuses of a granule by asking for granule + collection similar to current endpoint asking for operation-id
4. Consider the possibility of 1 source collection being sent to different DAACs and DAAC having the same collection ID on their side. This will currently fail.
5. Verify if 1 CNM message can accept 1 file only or a complete set of data, metadata, qc files (3 files)
6. Use SNS Batch Send to alleviate pressure on SNS calls, but this will complicate database entries for audit, and complicate failure handling. 
