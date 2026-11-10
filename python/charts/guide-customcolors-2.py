# Pass a list of Colors
custom_colors = ["#D62728", "#2CA02C", "#1F77B4", "#9467BD", "#FF7F0E", "#17BECF"]

# A dict from group to color
custom_colors = dict(zip(ophA_cluster["class"].unique(), custom_colors))

(GC(ophA_cluster, group="class", height="100px").color(custom_colors=custom_colors))
