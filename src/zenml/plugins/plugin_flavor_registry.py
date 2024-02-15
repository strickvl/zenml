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
"""Registry for all plugins."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Type

from pydantic import BaseModel

from zenml.enums import PluginSubType, PluginType
from zenml.integrations.registry import integration_registry
from zenml.logger import get_logger
from zenml.models import Page
from zenml.plugins.base_plugin_flavor import BasePlugin, BasePluginFlavor

logger = get_logger(__name__)
if TYPE_CHECKING:
    from zenml.models.v2.base.base_plugin_flavor import (
        BasePluginFlavorResponse,
    )


class RegistryEntry(BaseModel):
    """Registry Entry Class for the Plugin Registry."""

    flavor_class: Type[BasePluginFlavor[Any]]
    plugin_instance: Optional[BasePlugin]

    class Config:
        """Pydantic configuration class."""

        arbitrary_types_allowed = True


class PluginFlavorRegistry:
    """Registry for plugin flavors."""

    def __init__(self) -> None:
        """Initialize the event flavor registry."""
        self.plugin_flavors: Dict[
            PluginType, Dict[PluginSubType, Dict[str, RegistryEntry]]
        ] = {}
        self.register_plugin_flavors()

    @property
    def _types(self) -> List[PluginType]:
        """Returns all available flavors."""
        return list(self.plugin_flavors.keys())

    def list_subtypes_within_type(
        self, _type: PluginType
    ) -> List[PluginSubType]:
        """Returns all available subtypes for a given type.

        Args:
            _type: The type of plugin

        Returns:
            A list of available plugin subtypes for this plugin type.

        Raises:
            KeyError: If the type has no registry entries.
        """
        return list(self.plugin_flavors[_type].keys())

    def _flavor_entries(
        self, _type: PluginType, subtype: PluginSubType
    ) -> Dict[str, RegistryEntry]:
        """Get a list of all subtypes for a specific flavor and type.

        Args:
            _type: The type of Plugin
            subtype: The subtype of the plugin
        """
        if (
            _type in self.plugin_flavors
            and subtype in self.plugin_flavors[_type]
        ):
            return self.plugin_flavors[_type][subtype]
        else:
            return {}

    def list_available_flavor_names_for_type_and_subtype(
        self,
        _type: PluginType,
        subtype: PluginSubType,
        page: int,
        size: int,
    ) -> List[str]:
        """Get a list of all subtypes for a specific flavor and type.

        Args:
            _type: The type of Plugin
            subtype: The subtype of the plugin
            page: For optional pagination
            size: For optional pagination
        """
        flavor_names = list(
            self._flavor_entries(_type=_type, subtype=subtype).keys()
        )
        if page > 0 and size > 0:
            start = page * size
            end = start + size
            return flavor_names[start:end]
        else:
            raise RuntimeError(
                f"Invalid pagination values. Both values for "
                f"page: {page} and size: {size} need to be "
                f"positive, non-zero integers."
            )

    def list_available_flavors_for_type_and_subtype(
        self,
        _type: PluginType,
        subtype: PluginSubType,
    ) -> List[Type[BasePluginFlavor[Any]]]:
        """Get a list of all subtypes for a specific flavor and type.

        Args:
            _type: The type of Plugin
            subtype: The subtype of the plugin
        """
        flavors = list(
            [
                entry.flavor_class
                for _, entry in self._flavor_entries(
                    _type=_type, subtype=subtype
                ).items()
            ]
        )
        return flavors

    def list_available_flavor_responses_for_type_and_subtype(
        self,
        _type: PluginType,
        subtype: PluginSubType,
        page: int,
        size: int,
        hydrate: bool = False,
    ) -> Page[BasePluginFlavorResponse[Any, Any, Any]]:
        """Get a list of all subtypes for a specific flavor and type.

        Args:
            _type: The type of Plugin
            subtype: The subtype of the plugin
            page: Page for pagination (offset +1)
            size: Page size for pagination
            hydrate: Whether to hydrate the response bodies

        Returns:
            A page of flavors.
        """
        flavors = self.list_available_flavors_for_type_and_subtype(
            _type=_type,
            subtype=subtype,
        )
        total = len(flavors)
        total_pages = total / size
        start = (page - 1) * size
        end = start + size

        page_items = [
            flavor.get_flavor_response_model(hydrate=hydrate)
            for flavor in flavors
        ][start:end]

        return_page = Page(
            index=page,
            max_size=size,
            total_pages=total_pages,
            total=total,
            items=page_items,
        )
        return return_page

    @property
    def _builtin_flavors(self) -> Sequence[Type["BasePluginFlavor[Any]"]]:
        """A list of all default in-built flavors.

        Returns:
            A list of builtin flavors.
        """
        from zenml.actions.pipeline_run.pipeline_run_action import (
            PipelineRunActionFlavor,
        )
        from zenml.scheduler.scheduler_event_source_flavor import (
            SchedulerEventSourceFlavor,
        )

        flavors = [SchedulerEventSourceFlavor, PipelineRunActionFlavor]
        return flavors

    @property
    def _integration_flavors(self) -> Sequence[Type["BasePluginFlavor[Any]"]]:
        """A list of all integration event flavors.

        Returns:
            A list of integration flavors.
        """
        # TODO: Only load active integrations
        integrated_flavors = []
        for _, integration in integration_registry.integrations.items():
            for flavor in integration.plugin_flavors():
                integrated_flavors.append(flavor)

        return integrated_flavors

    def _get_registry_entry(
        self,
        _type: PluginType,
        subtype: PluginSubType,
        flavor_name: str,
    ) -> RegistryEntry:
        """Get registry entry.

        Args:
            _type: Type of the entry.
            subtype: Subtype of the entry.
            flavor_name: Flavor of the entry.

        Returns:
            The registry entry.

        Raises:
            KeyError: In case no entry exists.
        """
        return self.plugin_flavors[_type][subtype][flavor_name]

    def register_plugin_flavors(self) -> None:
        """Registers all flavors."""
        for flavor in self._builtin_flavors:
            self.register_plugin_flavor(flavor_class=flavor)
        for flavor in self._integration_flavors:
            self.register_plugin_flavor(flavor_class=flavor)

    def register_plugin_flavor(
        self, flavor_class: Type[BasePluginFlavor[Any]]
    ) -> None:
        """Registers a new event_source.

        Args:
            flavor_class: The flavor to register
        """
        try:
            self._get_registry_entry(
                _type=flavor_class.TYPE,
                subtype=flavor_class.SUBTYPE,
                flavor_name=flavor_class.FLAVOR,
            )
        except KeyError:
            (
                self.plugin_flavors.setdefault(flavor_class.TYPE, {})
                .setdefault(flavor_class.SUBTYPE, {})
                .setdefault(
                    flavor_class.FLAVOR,
                    RegistryEntry(flavor_class=flavor_class),
                )
            )
            logger.debug(
                f"Registered built in plugin {flavor_class.FLAVOR} for "
                f"plugin type {flavor_class.TYPE} and "
                f"subtype {flavor_class.SUBTYPE}: {flavor_class}"
            )
        else:
            logger.debug(
                f"Found existing flavor {flavor_class.FLAVOR} already "
                f"registered for this type {flavor_class.TYPE} and subtype "
                f"{flavor_class.SUBTYPE}. "
                f"Skipping registration for {flavor_class}."
            )

    def get_flavor_class(
        self,
        _type: PluginType,
        subtype: PluginSubType,
        name: str,
    ) -> Type[BasePluginFlavor[Any]]:
        """Get a single event_source based on the key.

        Args:
            _type: The type of plugin.
            subtype: The subtype of plugin.
            name: Indicates the name of the plugin flavor.

        Returns:
            `BaseEventConfiguration` subclass that was registered for this key.
        """
        try:
            return self._get_registry_entry(
                _type=_type,
                subtype=subtype,
                flavor_name=name,
            ).flavor_class
        except KeyError:
            raise KeyError(
                f"No flavor class found for flavor name {name} at type "
                f"{_type} and subtype {subtype}."
            )

    def get_plugin(
        self,
        _type: PluginType,
        subtype: PluginSubType,
        name: str,
    ) -> "BasePlugin":
        """Get the plugin based on the flavor, type and subtype.

        Args:
            name: The name of the plugin flavor.
            _type: The type of plugin.
            subtype: The subtype of plugin.

        Returns:
            Plugin instance associated with the flavor, type and subtype.

        Raises:
            KeyError: If no plugin is found for the given flavor, type and
                subtype.
            RuntimeError: If the plugin was not initialized.
        """
        try:
            plugin_entry = self._get_registry_entry(
                _type=_type,
                subtype=subtype,
                flavor_name=name,
            )
            if plugin_entry.plugin_instance is None:
                raise RuntimeError(
                    f"Plugin {plugin_entry.flavor_class} was not initialized."
                )
            return plugin_entry.plugin_instance
        except KeyError:
            raise KeyError(
                f"No flavor found for flavor name {name} and type "
                f"{_type} and subtype {subtype}."
            )

    def initialize_plugins(self) -> None:
        """Initializes all registered plugins."""
        for _, subtypes_dict in self.plugin_flavors.items():
            for _, flavor_dict in subtypes_dict.items():
                for _, registry_entry in flavor_dict.items():
                    # TODO: Only initialize if the integration is active
                    registry_entry.plugin_instance = (
                        registry_entry.flavor_class.PLUGIN_CLASS()
                    )


plugin_flavor_registry = PluginFlavorRegistry()
