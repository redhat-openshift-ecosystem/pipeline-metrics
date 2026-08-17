"""
Tekton modules that parses a Tekton resources
"""

from typing import Literal, Annotated
from datetime import datetime, UTC
from pydantic import BaseModel, Field


class Labels(BaseModel):
    """
    Model for PipelineRun labels.
    """

    pipeline_name: Annotated[str, Field(alias="tekton.dev/pipeline")]


class Metadata(BaseModel):
    """
    Model for PipelineRun metadata.
    """

    labels: Labels
    name: str
    namespace: str


class Condition(BaseModel):
    """
    Model for PipelineRun status conditions.
    """

    status: Literal["True", "False"]


class Status(BaseModel):
    """
    Model for PipelineRun status.
    """

    start_time: Annotated[datetime, Field(alias="startTime")]
    end_time: Annotated[datetime | None, Field(alias="completionTime")]
    conditions: list[Condition] | None


class PipelineRun(BaseModel):
    """
    Model for PipelineRuns.
    """

    metadata: Metadata
    status_object: Annotated[Status, Field(alias="status")]

    @property
    def pipeline_name(self) -> str:
        """
        Pipeline name

        Returns:
            Any: Pipeline name
        """
        return self.metadata.labels.pipeline_name

    @property
    def pipelinerun_name(self) -> str:
        """
        Pipeline run name

        Returns:
            Any: Pipeline run name
        """
        return self.metadata.name

    @property
    def namespace(self) -> str:
        """
        Pipeline run namespace

        Returns:
            Any: Namespace where the pipelinerun was executed
        """
        return self.metadata.namespace

    @property
    def duration(self) -> float:
        """
        Pipeline run duration in seconds

        If pipeline hasn't finished yet a now() is used as an end date

        Returns:
            Any: Pipeline run duration in seconds
        """
        end_time = self.status_object.end_time or datetime.now(UTC)
        return (end_time - self.status_object.start_time).total_seconds()

    @property
    def status(self) -> Literal["success", "failed", "unknown"]:
        """
        Pipeline overall status

        Returns:
            str: Pipeline overall status based on status of individual tasks
        """
        conditions = self.status_object.conditions
        if not conditions:
            return "unknown"
        return "success" if conditions[0].status == "True" else "failed"
