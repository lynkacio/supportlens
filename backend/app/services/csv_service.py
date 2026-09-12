import csv
import io


REQUIRED_COLUMNS = {
    "ticket_id",
    "customer_message",
    "created_at",
}


def parse_ticket_csv(content: bytes) -> list[dict]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV file must be UTF-8 encoded") from exc

    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise ValueError("CSV file is empty or missing a header")

    columns = {
        column.strip()
        for column in reader.fieldnames
        if column is not None
    }

    missing_columns = REQUIRED_COLUMNS - columns

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    tickets = []

    for row in reader:
        # Ignore completely empty rows
        if not any(
            value and value.strip()
            for value in row.values()
        ):
            continue

        ticket = {
            "ticket_id": row["ticket_id"].strip(),
            "customer_message": row["customer_message"].strip(),
            "created_at": row["created_at"].strip(),
        }

        tickets.append(ticket)

    if not tickets:
        raise ValueError("CSV contains no ticket data")

    return tickets