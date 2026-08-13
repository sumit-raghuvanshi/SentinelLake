"""Build Spark analytics from SentinelLake curated IOC data."""

from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as functions


def parse_arguments() -> argparse.Namespace:
    """Read input and output paths from the command line."""

    parser = argparse.ArgumentParser(
        description="Build SentinelLake IOC analytics with PySpark."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to curated accepted_iocs.json.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory for Spark analytics output.",
    )
    return parser.parse_args()


def main() -> int:
    """Read curated IOCs and write Spark-generated analytics datasets."""

    arguments = parse_arguments()

    spark = (
        SparkSession.builder
        .appName("SentinelLake IOC Analytics")
        .getOrCreate()
    )

    try:
        accepted_iocs = (
            spark.read
            .option("multiLine", "true")
            .json(arguments.input)
        )

        ioc_type_counts = (
            accepted_iocs
            .groupBy("ioc_type")
            .count()
            .orderBy("ioc_type")
        )

        threat_category_counts = (
            accepted_iocs
            .select(
                functions.explode("threat_categories").alias(
                    "threat_category"
                )
            )
            .groupBy("threat_category")
            .count()
            .orderBy(
                functions.desc("count"),
                functions.asc("threat_category"),
            )
        )

        summary = accepted_iocs.agg(
            functions.count("*").alias("unique_iocs"),
            functions.round(
                functions.avg("confidence_score"),
                2,
            ).alias("average_confidence_score"),
            functions.sum("source_count").alias(
                "total_source_observations"
            ),
        )

        ioc_type_counts.coalesce(1).write.mode("overwrite").json(
            f"{arguments.output}/ioc_type_counts"
        )
        threat_category_counts.coalesce(1).write.mode("overwrite").json(
            f"{arguments.output}/threat_category_counts"
        )
        summary.coalesce(1).write.mode("overwrite").json(
            f"{arguments.output}/summary"
        )

        summary_row = summary.first()

        print("SentinelLake Spark Analytics")
        print("-----------------------------")
        print(f"Unique IOCs analysed: {summary_row['unique_iocs']}")
        print(
            "Average confidence score: "
            f"{summary_row['average_confidence_score']}"
        )
        print(
            "Total source observations: "
            f"{summary_row['total_source_observations']}"
        )
        print(f"Spark output saved: {arguments.output}")

        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main())