import pathlib
import libcst as cst


class AddDocstrings(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node, updated_node):
        # Only add docstrings to public functions
        if original_node.name.value.startswith("_"):
            return updated_node

        # Skip functions that already have a docstring
        if original_node.body.body:
            first = original_node.body.body[0]

            if (
                isinstance(first, cst.SimpleStatementLine)
                and first.body
                and isinstance(first.body[0], cst.Expr)
                and isinstance(first.body[0].value, cst.SimpleString)
            ):
                return updated_node

        docstring = cst.SimpleStatementLine(
            body=[
                cst.Expr(
                    value=cst.SimpleString(
                        f'"{original_node.name.value.replace("_", " ").capitalize()}."'
                    )
                )
            ]
        )

        new_body = [docstring] + list(updated_node.body.body)

        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=new_body)
        )


for path in pathlib.Path("src").rglob("*.py"):
    source = path.read_text(encoding="utf-8")

    try:
        module = cst.parse_module(source)
        updated = module.visit(AddDocstrings())

        if updated.code != source:
            path.write_text(updated.code, encoding="utf-8")
            print(f"Updated: {path}")

    except Exception as exc:
        print(f"ERROR: {path} -> {exc}")

print("\nDocstring insertion complete.")