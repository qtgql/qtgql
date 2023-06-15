from __future__ import annotations

from typing import TYPE_CHECKING

import graphql

from qtgqlcodegen.core.exceptions import QtGqlException
from qtgqlcodegen.core.template import CmakeTemplateContext, cmake_template
from qtgqlcodegen.operation.evaluation import evaluate_operations
from qtgqlcodegen.operation.template import OperationTemplateContext
from qtgqlcodegen.schema.evaluation import evaluate_schema
from qtgqlcodegen.schema.template import (
    SchemaTemplateContext,
    operation_template,
    schema_types_template_cpp,
    schema_types_template_hpp,
)
from qtgqlcodegen.types import BuiltinScalars
from qtgqlcodegen.utils import FileSpec

if TYPE_CHECKING:
    from qtgqlcodegen.config import QtGqlConfig


class SchemaGenerator:
    def __init__(self, config: QtGqlConfig, schema: graphql.GraphQLSchema):
        self.gql_schema = schema
        self.config = config
        self.schema_type_info = evaluate_schema(schema, self.config.custom_scalars)

    def generate(self) -> list[FileSpec]:
        operations: list[FileSpec] = self._generate_operations()
        context = SchemaTemplateContext(
            enums=list(self.schema_type_info.enums.values()),
            types=[
                t
                for name, t in self.schema_type_info.object_types.items()
                if name not in BuiltinScalars.keys
                and name not in self.schema_type_info.root_types_names
            ],
            interfaces=list(self.schema_type_info.interfaces.values()),
            input_objects=list(self.schema_type_info.input_objects.values()),
            config=self.config,
        )
        schema_hpp = FileSpec(
            content=schema_types_template_hpp(context),
            path=self.config.generated_dir / "schema.hpp",
        )
        schema_cpp = FileSpec(
            content=schema_types_template_cpp(context),
            path=self.config.generated_dir / "schema.cpp",
        )

        return [schema_hpp, schema_cpp, *operations]

    def _generate_operations(self) -> list[FileSpec]:
        operations_document = graphql.parse(self.config.operations_dir.read_text())

        # validate the operation against the static schema
        if errors := graphql.validate(self.gql_schema, operations_document):
            raise QtGqlException([error.formatted for error in errors])

        operations = evaluate_operations(operations_document, self.schema_type_info)

        return [
            FileSpec(
                content=operation_template(
                    OperationTemplateContext(
                        operation=op,
                        config=self.config,
                        debug=self.config.debug,
                    ),
                ),
                path=self.config.generated_dir / f"{op_name}.hpp",
            )
            for op_name, op in operations.items()
        ]

    def dump(self):
        """:param file: Path to the directory the codegen would dump to."""
        sources = self.generate()

        cmake = FileSpec(
            content=cmake_template(CmakeTemplateContext(config=self.config, sources=sources)),
            path=self.config.generated_dir / "CMakeLists.txt",
        )
        sources.append(cmake)
        for f in sources:
            f.dump()
