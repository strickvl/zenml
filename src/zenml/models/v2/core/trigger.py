#  Copyright (c) ZenML GmbH 2024. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""Collection of all models concerning triggers."""
from typing import TYPE_CHECKING, Any, Dict, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field

from zenml.constants import STR_FIELD_MAX_LENGTH
from zenml.models.v2.base.base import BaseZenModel
from zenml.models.v2.base.scoped import (
    WorkspaceScopedFilter,
    WorkspaceScopedRequest,
    WorkspaceScopedResponse,
    WorkspaceScopedResponseBody,
    WorkspaceScopedResponseMetadata,
    WorkspaceScopedResponseResources,
)

if TYPE_CHECKING:
    from zenml.models.v2.core.event_source import EventSourceResponse
    from zenml.zen_stores.schemas import BaseSchema

    AnySchema = TypeVar("AnySchema", bound=BaseSchema)

# ------------------ Base Model ------------------


class TriggerBase(BaseModel):
    """Base model for triggers."""

    name: str = Field(
        title="The name of the Trigger.", max_length=STR_FIELD_MAX_LENGTH
    )
    description: str = Field(
        default="",
        title="The description of the trigger",
        max_length=STR_FIELD_MAX_LENGTH,
    )
    event_source_id: UUID = Field(
        title="The event source that activates this trigger.",
    )
    event_filter: Dict[str, Any] = Field(
        title="Filter applied to events that activate this trigger.",
    )

    action: Dict[str, Any] = Field(
        title="The configuration for the action that is executed by this "
        "trigger.",
    )
    action_flavor: str = Field(
        title="The flavor of the action that is executed by this trigger.",
        max_length=STR_FIELD_MAX_LENGTH,
    )
    action_subtype: str = Field(
        title="The subtype of the action that is executed by this trigger.",
        max_length=STR_FIELD_MAX_LENGTH,
    )


# ------------------ Request Model ------------------
class TriggerRequest(TriggerBase, WorkspaceScopedRequest):
    """Model for creating a new Trigger."""

    # executions: somehow we need to link to executed Actions here


# ------------------ Update Model ------------------


class TriggerUpdate(BaseZenModel):
    """Update model for triggers."""

    name: Optional[str] = Field(
        default=None,
        title="The new name for the Trigger.",
        max_length=STR_FIELD_MAX_LENGTH,
    )
    description: Optional[str] = Field(
        default=None,
        title="The new description for the trigger",
        max_length=STR_FIELD_MAX_LENGTH,
    )
    event_filter: Optional[Dict[str, Any]] = Field(
        default=None,
        title="New filter applied to events that activate this trigger.",
    )
    action: Optional[Dict[str, Any]] = Field(
        default=None,
        title="The new configuration for the action that is executed by this "
        "trigger.",
    )
    is_active: Optional[bool] = Field(
        default=None,
        title="The new status of the trigger.",
    )


# ------------------ Response Model ------------------


class TriggerResponseBody(WorkspaceScopedResponseBody):
    """ResponseBody for triggers."""

    event_source_flavor: str
    action_flavor: str
    action_subtype: str

    is_active: bool


class TriggerResponseMetadata(WorkspaceScopedResponseMetadata):
    """Response metadata for triggers."""

    event_filter: Dict[str, Any] = Field(
        title="The event that activates this trigger.",
    )
    action: Dict[str, Any] = Field(
        title="The action that is executed by this trigger.",
    )
    description: str = Field(
        default="",
        title="The description of the trigger",
        max_length=STR_FIELD_MAX_LENGTH,
    )


class TriggerResponseResources(WorkspaceScopedResponseResources):
    """Class for all resource models associated with the trigger entity."""

    event_source: "EventSourceResponse" = Field(
        title="The event source that activates this trigger.",
    )


class TriggerResponse(
    WorkspaceScopedResponse[
        TriggerResponseBody, TriggerResponseMetadata, TriggerResponseResources
    ]
):
    """Response model for models."""

    name: str = Field(
        title="The name of the model",
        max_length=STR_FIELD_MAX_LENGTH,
    )

    def get_hydrated_version(self) -> "TriggerResponse":
        """Get the hydrated version of this trigger.

        Returns:
            An instance of the same entity with the metadata field attached.
        """
        from zenml.client import Client

        return Client().zen_store.get_trigger(self.id)

    @property
    def event_source_flavor(self) -> str:
        """The `event_source_flavor` property.

        Returns:
            the value of the property.
        """
        return self.get_body().event_source_flavor

    @property
    def action_flavor(self) -> str:
        """The `action_flavor` property.

        Returns:
            the value of the property.
        """
        return self.get_body().action_flavor

    @property
    def event_filter(self) -> Dict[str, Any]:
        """The `event_filter` property.

        Returns:
            the value of the property.
        """
        return self.get_metadata().event_filter

    @property
    def action(self) -> Dict[str, Any]:
        """The `action` property.

        Returns:
            the value of the property.
        """
        return self.get_metadata().action

    @property
    def description(self) -> str:
        """The `description` property.

        Returns:
            the value of the property.
        """
        return self.get_metadata().description

    @property
    def event_source(self) -> "EventSourceResponse":
        """The `event_source` property.

        Returns:
            the value of the property.
        """
        return self.get_resources().event_source


# ------------------ Filter Model ------------------


class TriggerFilter(WorkspaceScopedFilter):
    """Model to enable advanced filtering of all TriggerModels."""

    name: Optional[str] = Field(
        default=None,
        description="Name of the trigger",
    )
    event_source_id: Optional[Union[UUID, str]] = Field(
        default=None,
        description="By the event source this trigger is attached to.",
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether the trigger is active.",
    )
    action_flavor: Optional[str] = Field(
        default=None,
        title="The flavor of the action that is executed by this trigger.",
    )
    action_subtype: Optional[str] = Field(
        default=None,
        title="The subtype of the action that is executed by this trigger.",
    )
    # TODO: Ignore these in normal filter and handle in sqlzenstore
    resource_id: Optional[Union[UUID, str]] = Field(
        default=None,
        description="By the resource this trigger references.",
    )
    resource_type: Optional[str] = Field(
        default=None,
        description="By the resource type this trigger references.",
    )
