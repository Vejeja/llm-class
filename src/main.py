import argparse
from monitoring_dashboard import (
    ModelFactory,
    IntentParser,
    MetricRetriever,
    PromQLBuilder,
)

class DummyDB:
    def query(self, vector, top_k=5):
        return [
            {"metric": "node_cpu_seconds_total"},
            {"metric": "node_memory_MemAvailable_bytes"}
        ]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Запрос на естественном языке")
    parser.add_argument(
        "--override",
        nargs="*",
        help="Override моделей: intent=..., embedding=..."
    )
    args = parser.parse_args()

    override = dict(item.split("=", 1) for item in (args.override or []))
    factory = ModelFactory(override)

    intent = IntentParser(factory).parse(args.query)
    desc   = intent["entities"]["metric_description_query"]
    metrics = MetricRetriever(factory, DummyDB()).retrieve(desc)

    result = PromQLBuilder(factory).build(intent, metrics)

    print("PromQL:", result["response"]["query"])
    print("Reasoning:", result["reasoning"])

if __name__ == "__main__":
    main()
