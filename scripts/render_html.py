"""Generate the local HTML entry point and individual interactive exports."""
from pathlib import Path
import html
import re

VIEWS=[('overview','Overview and tables','index.html'),('cities','Cities and appointments','maps/cities.html'),('choropleth','States and provinces','maps/choropleths.html'),('flows','Birth, education, work','maps/flows.html'),('bipartite','Students and employers','networks/individual_employer.html'),('projection','Employer network','networks/employer_projection.html'),('sankey','Past and current employers','sankey/employers.html')]
def build_pages(root,metrics):
    for view,title,path in VIEWS:
        prefix='' if view=='overview' else '../'
        nav=''.join(f'<a class="{"active" if v==view else ""}" href="{prefix}{p}">{html.escape(t)}</a>' for v,t,p in VIEWS)
        page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | Student careers</title>
<link rel="stylesheet" href="{prefix}assets/leaflet.css"><link rel="stylesheet" href="{prefix}assets/style.css">
<script src="{prefix}assets/analysis_data.js"></script><script src="{prefix}assets/ui_helpers.js"></script><script src="{prefix}assets/leaflet.js"></script><script src="{prefix}assets/vis-network.min.js"></script><script src="{prefix}assets/plotly.min.js"></script></head>
<body data-view="{view}"><header><div><span class="eyebrow">HISTORICAL STUDENT CAREERS</span><h1>{title}</h1><p>Recorded affiliations, origins and education. Appointment status refers to the historical source.</p></div><a href="{prefix}README.html">Methods and files ↗</a></header><nav>{nav}</nav>
<div class="layout"><aside><div class="filterhead"><h2>Filter records</h2><button id="reset">Reset</button></div><p class="muted">Choices within a filter are combined with OR; filters are combined with AND. All choices start selected.</p><div id="filters"></div>
<fieldset><legend>Period</legend><label>Basis<select id="periodBasis"><option value="birth_year">Year of birth</option><option value="study_start">First recorded study year</option><option value="study_end">Last recorded study year</option><option value="study_overlap" selected>Recorded study span overlaps</option></select></label><div class="range"><label>From<input id="yearMin" type="number" value="1876"></label><label>To<input id="yearMax" type="number" value="1944"></label></div><label class="check"><input id="unknownYears" type="checkbox" checked> Include unknown years</label></fieldset><div id="special"></div><button class="primary" id="apply">Apply filters</button><p class="muted">Study bounds are the earliest and latest recorded education years, not confirmed attendance dates.</p></aside>
<main><div id="kpis" class="kpis"></div><p id="notice" class="notice"></p><div id="viewControls" class="toolbar"></div><div id="visual"></div><div id="legend"></div><div id="detail"></div><footer>Offline HTML. Counts describe recorded appointments; missing career records do not establish unemployment. Modern boundaries are reference outlines for historical places.</footer></main></div><script src="{prefix}assets/app.js"></script></body></html>'''
        # Inline assets so each exported HTML is independently portable and offline.
        def script(match):
            name=match.group(1).split('/')[-1]
            if name=='plotly.min.js' and view!='sankey': return ''
            if name=='vis-network.min.js' and view not in ['bipartite','projection']: return ''
            if name=='leaflet.js' and view not in ['cities','choropleth','flows']: return ''
            body=(root/'assets'/name).read_text(encoding='utf-8')
            return '<script>'+re.sub(r'</script',r'<\\/script',body,flags=re.I)+'</script>'
        page=re.sub(r'<script src="([^"]+)"></script>',script,page)
        page=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(root/'assets'/m.group(1).split('/')[-1]).read_text()+'</style>',page)
        (root/path).write_text(page,encoding='utf-8')
