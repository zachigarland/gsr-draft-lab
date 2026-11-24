def apply(h):
    def sub(a,b):
        assert h.count(a)>=1, a
        return h.replace(a,b)
    h = sub("--ink:#000D1A; --panel:#071A2E; --panel-2:#0B2239; --line:#17344F;",
            "--ink:#FFFFFF; --panel:#F6F8FB; --panel-2:#EDF1F6; --line:#DCE3EB; --navy:#0B2239; --blue:#1F5FA8;")
    h = sub("--fg:#E9EFF5; --muted:#8FA3B8; --accent:#EC540B; --accent-soft:rgba(236,84,11,.16);",
            "--fg:#0E1A26; --muted:#5A6878; --accent:#E2500A; --accent-soft:rgba(226,80,10,.09);")
    h = sub("--tA:#F2B138; --tB:#5AA9E6; --tC:#6CC08B; --tD:#7C8DA0; --tW:#A393E0;",
            "--tA:#E2500A; --tB:#1F5FA8; --tC:#2E8B57; --tD:#6B7A8C; --tW:#7B61C9;")
    h = sub("--up:#6CC08B; --down:#E8736B;", "--up:#1E8E4F; --down:#C8382E;")
    h = h.replace("#1E4466", "#B9CBE0")
    extra = """
<style id="gsr-light">
body{background:#fff;color:var(--fg)}
header, .hero{border-bottom:4px solid var(--navy)}
h1 .acc, .accent{color:var(--accent)}
.rail .o{background:var(--navy)!important;opacity:.7!important}
a{color:var(--blue)}
.toast{background:var(--navy)!important;color:#fff!important}
</style>
"""
    h = sub("</head>", extra + "</head>")
    return h
