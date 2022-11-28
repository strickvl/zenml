#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
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

import os
import shutil
from typing import Any, Callable, Optional, Type

from zenml.artifacts.data_artifact import DataArtifact
from zenml.constants import ENV_ZENML_DEBUG
from zenml.materializers.base_materializer import BaseMaterializer
from zenml.materializers.default_materializer_registry import (
    default_materializer_registry,
)


def test_handle_int_env_var():
    """Checks that the ZENML_DEBUG is set in the tests."""
    assert os.environ[ENV_ZENML_DEBUG] == "true"


def _test_materializer(
    step_output: Any,
    step_output_type: Optional[Type[Any]] = None,
    materializer_class: Optional[Type[BaseMaterializer]] = None,
    artifact_uri: Optional[str] = None,
    validation_function: Optional[Callable[[str], Any]] = None,
) -> Any:
    """Test whether the materialization of a given step output works.

    To do so, we first materialize the output to disk, then read it again with
    the same materializer and ensure that:
    - `materializer.handle_return()` did write something to disk
    - `materializer.handle_input()` did load the original data type again

    Args:
        step_output: The output artifact we want to materialize.
        step_output_type: The type of the output artifact. If not provided,
            `type(step_output)` will be used.
        materializer_class: The materializer class. If not provided, we query
            the default materializer registry using `step_output_type`.
        artifact_uri: An optional URI to assign to the artifact that will be
            materialized.
        validation_function: An optional function to call on the absolute path
            to `artifact_uri`. Can be used, e.g., to check whether a certain
            file exists or a certain number of files were written.

    Returns:
        The result of materializing `step_output` to disk and loading it again.
    """
    if step_output_type is None:
        step_output_type = type(step_output)

    if materializer_class is None:
        materializer_class = default_materializer_registry[step_output_type]

    mock_artifact = DataArtifact(uri=artifact_uri or "")
    materializer = materializer_class(mock_artifact)
    data_path = os.path.abspath(mock_artifact.uri)
    existing_files = os.listdir(data_path)
    try:
        materializer.handle_return(step_output)
        new_files = os.listdir(data_path)
        assert len(new_files) > len(existing_files)  # something was written
        loaded_data = materializer.handle_input(step_output_type)
        assert isinstance(loaded_data, step_output_type)  # correct type
        if validation_function:
            validation_function(data_path)
        return loaded_data
    finally:
        new_files = os.listdir(data_path)
        created_files = [
            filename for filename in new_files if filename not in existing_files
        ]
        for filename in created_files:
            full_path = os.path.join(data_path, filename)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
