from .data.integration import DataIntegrator, load_csv_rows

__version__ = "0.1.0"


def hello() -> str:
    """Return a simple greeting used by the demo test."""
    return "Hello, Aria!"


__all__ = ["hello", "__version__", "DataIntegrator", "load_csv_rows"]


if __name__ == "__main__":
    print(hello())
