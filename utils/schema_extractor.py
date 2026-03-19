import sqlalchemy as sa
import pandas as pd


def get_schema_from_engine(engine) -> str:
    inspector = sa.inspect(engine)
    table_names = inspector.get_table_names()

    if not table_names:
        return "No tables found in this database."

    schema_lines = []

    for table in table_names:
        columns = inspector.get_columns(table)
        pk_constraint = inspector.get_pk_constraint(table)
        foreign_keys = inspector.get_foreign_keys(table)

        pk_columns = pk_constraint.get("constrained_columns", [])
        fk_map = {
            fk["constrained_columns"][0]: fk["referred_table"]
            for fk in foreign_keys
            if fk["constrained_columns"]
        }

        schema_lines.append(f"Table: {table}")
        schema_lines.append("Columns:")

        for col in columns:
            col_name = col["name"]
            col_type = str(col["type"])
            markers = []

            if col_name in pk_columns:
                markers.append("PRIMARY KEY")
            if col_name in fk_map:
                markers.append(f"FK -> {fk_map[col_name]}")
            if not col.get("nullable", True):
                markers.append("NOT NULL")

            marker_str = "  [" + ", ".join(markers) + "]" if markers else ""
            schema_lines.append(f"    {col_name} {col_type}{marker_str}")

        schema_lines.append("")

    return "\n".join(schema_lines)


def get_table_preview(engine, table_name: str, limit: int = 5) -> pd.DataFrame:
    with engine.connect() as conn:
        result = conn.execute(
            sa.text(f"SELECT * FROM {table_name} LIMIT {limit}")
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df