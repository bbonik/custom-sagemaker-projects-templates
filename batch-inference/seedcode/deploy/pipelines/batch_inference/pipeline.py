import os

import boto3
import sagemaker
from sagemaker import model
import sagemaker.session
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
)
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import (
    TransformStep, 
    Transformer, 
    TransformInput
)


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def get_sagemaker_client(region):
     """Gets the sagemaker client.

        Args:
            region: the aws region to start the session
            default_bucket: the bucket to use for storing the artifacts

        Returns:
            `sagemaker.session.Session instance
        """
     boto_session = boto3.Session(region_name=region)
     sagemaker_client = boto_session.client("sagemaker")
     return sagemaker_client

def get_session(region, default_bucket=None):
    """Gets the sagemaker session based on the region.

    Args:
        region: the aws region to start the session
        default_bucket: the bucket to use for storing the artifacts

    Returns:
        `sagemaker.session.Session instance
    """

    boto_session = boto3.Session(region_name=region)

    sagemaker_client = boto_session.client("sagemaker")
    runtime_client = boto_session.client("sagemaker-runtime")
    return sagemaker.session.Session(
        boto_session=boto_session,
        sagemaker_client=sagemaker_client,
        sagemaker_runtime_client=runtime_client,
        default_bucket=default_bucket,
    )

def get_pipeline_custom_tags(new_tags, region, sagemaker_project_arn=None):
    try:
        sm_client = get_sagemaker_client(region)
        response = sm_client.list_tags(
            ResourceArn=sagemaker_project_arn)
        project_tags = response["Tags"]
        for project_tag in project_tags:
            new_tags.append(project_tag)
    except Exception as e:
        print(f"Error getting project tags: {e}")
    return new_tags

def get_pipeline(
    region,
    pipeline_name="AbalonePipelineBatchInference",
    base_job_prefix="Abalone",
):
    """Gets a SageMaker ML Pipeline instance working with on abalone data.

    Args:
        region: AWS region to create and run the pipeline.
        model_name: Name of the SageMaker Model to deploy

    Returns:
        an instance of a pipeline
    """
    sagemaker_session = get_session(region)

    #### PARAMETERS
    model_name = ParameterString("ModelName", default_value='${ModelName}')
    batch_inference_instance_count = ParameterInteger("BatchInstanceCount", default_value=1)
    batch_inference_instance_type = ParameterString("BatchInstanceType", default_value='ml.m5.large')
    input_path = ParameterString("InputPath", default_value=f"s3://sagemaker-servicecatalog-seedcode-{region}/dataset/abalone-dataset.csv")
    output_path = ParameterString("OutputPath")

    #### SAGEMAKER CONSTRUCTS
    transform = Transformer(
        model_name=model_name,
        instance_count=batch_inference_instance_count,
        instance_type=batch_inference_instance_type,
        output_path=output_path,
        base_transform_job_name=f"{base_job_prefix}/batch-transform-job",
        max_payload=10,
        accept='text/csv'
    )

    #### STEPS
    transform_step = TransformStep(
        name='BatchInferenceStep',
        transformer=transform,
        inputs=TransformInput(data=input_path, content_type='text/csv')
    )

    #### PIPELINE
    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[model_name, batch_inference_instance_count, batch_inference_instance_type, input_path, output_path],
        steps=[transform_step],
        sagemaker_session=sagemaker_session
    )
    return pipeline

    
