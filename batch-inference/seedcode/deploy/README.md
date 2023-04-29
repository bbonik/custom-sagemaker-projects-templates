# Custom MLOps template for Batch Inference with Batch Transform and SageMaker Pipelines

Guide to use this template:

1. Change the `*-config.json` files to the input path and output path that you want to use for batch inference. These should be S3 URIs.
2. Push the changes to CodeCommit from the SageMaker Studio IDE / your IDE of choice
3. Go to CodePipeline and check the pipeline related to the project.