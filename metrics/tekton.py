"""
Tekton modules that parses a Tekton resources
"""

from typing import Any
from datetime import datetime
from dateutil.parser import isoparse
import pytz


class PipelineRun:
    """
    Pipeline run object that stores basic info about pipeline run
    """

    def __init__(self, pipelinerun_data: Any) -> None:
        self.data = pipelinerun_data

    @property
    def metadata(self) -> Any:
        """
        Pipeline run metadata

        Returns:
            Any: Metadata section
        """
        return self.data.get("metadata", {})

    @property
    def pipeline_name(self) -> Any:
        """
        Pipeline name

        Returns:
            Any: Pipeline name
        """
        return self.metadata.get("labels", {}).get("tekton.dev/pipeline")

    @property
    def pipelinerun_name(self) -> Any:
        """
        Pipeline run name

        Returns:
            Any: Pipeline run name
        """
        return self.metadata.get("name")

    @property
    def namespace(self) -> Any:
        """
        Pipeline run namespace

        Returns:
            Any: Namespace where the pipelinerun was executed
        """
        return self.metadata.get("namespace")

    @property
    def duration(self) -> Any:
        """
        Pipeline run duration in seconds

        If pipeline hasn't finished yet a now() is used as a end date

        Returns:
            Any: Pipeline run duration in seconds
        """
        start_time = isoparse(self.data.get("status", {}).get("startTime"))
        end_time = self.data.get("status", {}).get("completionTime")
        if end_time:
            end_time = isoparse(end_time)
        else:
            end_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        return (end_time - start_time).total_seconds()

    @property
    def status(self) -> str:
        """
        Pipelina overall status

        Returns:
            str: Pipeline overall status based on status of individual tasks
        """
        conditions = self.data.get("status", {}).get("conditions", [])
        if not conditions:
            return "unknown"
        return "success" if conditions[0]["status"] == "True" else "failed"
