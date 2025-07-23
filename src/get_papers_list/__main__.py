import typer
from typing import Optional
from .papers import (
    fetch_pubmed_ids,
    fetch_pubmed_details,
    filter_papers_with_non_academic_authors,
    save_papers_to_csv
)
import sys
import csv
import os

app = typer.Typer(add_completion=False, help="Fetch PubMed papers with non-academic (pharma/biotech) authors.")

@app.command()
def main(
    query: str = typer.Argument(..., help="PubMed query string (use full PubMed syntax)"),
    file: Optional[str] = typer.Option(None, "-f", "--file", help="Filename to save results as CSV. If not provided, prints to console."),
    debug: bool = typer.Option(False, "-d", "--debug", help="Print debug information during execution."),
):
    """Fetch PubMed papers with at least one non-academic (pharma/biotech) author."""
    try:
        typer.echo("Fetching PubMed IDs...")
        ids = fetch_pubmed_ids(query, debug=debug)
        if not ids:
            typer.echo("No papers found for the given query.")
            raise typer.Exit(0)
        typer.echo(f"Found {len(ids)} papers. Fetching details...")
        papers = fetch_pubmed_details(ids, debug=debug)
        filtered = filter_papers_with_non_academic_authors(papers)
        if not filtered:
            typer.echo("No papers found with non-academic (pharma/biotech) authors.")
            raise typer.Exit(0)
        if file:
            # Always save to current working directory if just a filename is given
            abs_path = os.path.abspath(file)
            save_papers_to_csv(filtered, abs_path)
            typer.echo(f"Results saved to: {abs_path}")
        else:
            # Print as CSV to console
            fieldnames = [
                "PubmedID",
                "Title",
                "Publication Date",
                "Non-academicAuthor(s)",
                "CompanyAffiliation(s)",
                "Corresponding Author Email"
            ]
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            for paper in filtered:
                writer.writerow(paper)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 