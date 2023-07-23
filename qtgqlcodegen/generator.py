from __future__ import annotations

from typing import TYPE_CHECKING

import graphql
from attr import define

from qtgqlcodegen.core.exceptions import QtGqlException
from qtgqlcodegen.core.template import CmakeTemplateContext, cmake_template
from qtgqlcodegen.operation.evaluation import evaluate_operations
from qtgqlcodegen.operation.template import OperationTemplateContext
from qtgqlcodegen.schema.evaluation import evaluate_schema
from qtgqlcodegen.schema.template import (
    SchemaTemplateContext,
    operation_cpp_template,
    operation_hpp_template,
    schema_types_template_hpp,
)
from qtgqlcodegen.types import BuiltinScalars
from qtgqlcodegen.utils import FileSpec

if TYPE_CHECKING:
    from qtgqlcodegen.config import QtGqlConfig


@define
class OperationOutput:
    name: str
    sources: list[FileSpec]


@define
class GenerationOutput:
    schema: FileSpec
    operations: list[OperationOutput]

    def dump(self) -> None:
        self.schema.dump()
        for op in self.operations:
            for source in op.sources:
                source.dump()


class SchemaGenerator:
    def __init__(self, config: QtGqlConfig, schema: graphql.GraphQLSchema):
        self.gql_schema = schema
        self.config = config
        self.schema_type_info = evaluate_schema(schema, self.config.custom_scalars)

    def generate(self) -> GenerationOutput:
        operations = self._generate_operations()
        context = SchemaTemplateContext(
            enums=list(self.schema_type_info.enums.values()),
            types=[
                t
                for name, t in self.schema_type_info.object_types.items()
                if name not in BuiltinScalars.keys
            ],
            interfaces=list(self.schema_type_info.interfaces.values()),
            input_objects=list(self.schema_type_info.input_objects.values()),
            config=self.config,
        )
        schema_hpp = FileSpec(
            content=schema_types_template_hpp(context),
            path=self.config.generated_dir / "schema.hpp",
        )

        return GenerationOutput(
            schema=schema_hpp,
            operations=operations,
        )

    def _generate_operations(self) -> list[OperationOutput]:
        operations_document = graphql.parse(self.config.operations_dir.read_text("utf-8"))
        # validate the operation against the static schema
        if errors := graphql.validate(self.gql_schema, operations_document):
            raise QtGqlException([error.formatted for error in errors])

        operations = evaluate_operations(operations_document, self.schema_type_info)
        ret: list[OperationOutput] = []
        for op_name, op in operations.items():
            context = OperationTemplateContext(
                operation=op,
                config=self.config,
                debug=self.config.debug,
            )

            ret.append(
                OperationOutput(
                    name=op_name,
                    sources=[
                        FileSpec(
                            content=operation_hpp_template(context=context),
                            path=self.config.generated_dir / f"{op_name}.hpp",
                        ),
                        FileSpec(
                            content=operation_cpp_template(context=context),
                            path=self.config.generated_dir / f"{op_name}.cpp",
                        ),
                    ],
                ),
            )

        return ret

    def dump(self):
        generation_output = self.generate()

        cmake = FileSpec(
            content=cmake_template(
                CmakeTemplateContext(config=self.config, generation_output=generation_output),
            ),
            path=self.config.generated_dir / "CMakeLists.txt",
        )
        generation_output.dump()
        cmake.dump()
