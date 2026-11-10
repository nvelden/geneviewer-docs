# Example data for a single Gene cluster
ophA_cluster = ophA_clusters[ophA_clusters["cluster"] == "ophA"]

GC(ophA_cluster, start="start", end="end", group="class", height="150px")
