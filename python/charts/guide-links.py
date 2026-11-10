# Generate chart object
chart = GC(ophA_clusters, cluster="cluster", group="class", height="250px")
chart = chart.legend(False)

# Add links to chart
chart.links("class")
