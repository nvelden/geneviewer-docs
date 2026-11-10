links_data = pd.DataFrame(
    {
        "start1": [5000, 16000],
        "end1": [9000, 19000],
        "start2": [20000, 42000],
        "end2": [25000, 32000],
        "cluster1": ["ophA", "ophA"],
        "cluster2": ["dbophA", "dbophA"],
        "identity": [20, 100],
        "similarity": [10, 90],
    }
)

# Add links to chart
GC(ophA_clusters, cluster="cluster", group="class", height="250px").links(
    data=links_data, measure="identity", vmin=20, vmax=100
)
