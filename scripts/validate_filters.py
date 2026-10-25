from pathlib import Path
import json, random
import pandas as pd
root=Path(__file__).resolve().parent
j=pd.read_csv(root/'tables/career_joined.csv')
random.seed(13)
tests=[]
def scenario(name,filters={},basis='study_overlap',lo=1876,hi=1944,unknown=True):
    d=j.copy()
    for k,vs in filters.items():
        if k=='educationLevel':
            def level_matches(value):
                values=json.loads(value)
                return any(v in vs for v in (values or ['Unknown']))
            d=d[d.education_levels.map(level_matches)]
        else:d=d[d[k].isin(vs)]
    a=d.study_start if basis=='study_overlap' else d[basis]
    z=d.study_end if basis=='study_overlap' else a
    good=(a<=hi)&(z>=lo) if basis=='study_overlap' else (a>=lo)&(a<=hi)
    if unknown: good=good|a.isna()|z.isna()
    ids=d.loc[good,'record_id'].tolist()
    pairs={}
    for person,g in d.loc[good].groupby('NameID'):
        past=set(g.loc[g.status.eq('Past'),'employer'])-{'Unknown'}
        current=set(g.loc[g.status.eq('Current'),'employer'])-{'Unknown'}
        for a in past:
            for b in current:pairs.setdefault((a,b),set()).add(person)
    bridges=[{'source':'Past: '+a,'target':'Current: '+b,'NameIDs':sorted(ps),'individuals':len(ps)} for (a,b),ps in sorted(pairs.items())]
    tests.append({'name':name,'filters':filters,'basis':basis,'lo':lo,'hi':hi,'unknown':unknown,'expectedIDs':sorted(ids),'expectedSankey':bridges})
scenario('all')
scenario('current only',{'status':['Current']})
scenario('past and current',{'status':['Past','Current']})
scenario('empty status',{'status':[]})
scenario('multiple countries and sectors',{'country':['United States','China'],'sector':['Academic / education','Government / public administration']})
scenario('female current US',{'gender':['F'],'status':['Current'],'country':['United States']})
scenario('known birth years',basis='birth_year',unknown=False)
scenario('birth cohort plus unknown',basis='birth_year',lo=1910,hi=1919)
scenario('birth cohort only',basis='birth_year',lo=1910,hi=1919,unknown=False)
scenario('study overlap narrow',basis='study_overlap',lo=1940,hi=1940,unknown=False)
scenario('study start',basis='study_start',lo=1937,hi=1941,unknown=False)
scenario('study end',basis='study_end',lo=1943,hi=1944,unknown=False)
scenario('master level',{'educationLevel':['Master']})
scenario('multiple education levels',{'educationLevel':['Bachelor','Doctor']})
scenario('unknown education level',{'educationLevel':['Unknown']})
scenario('empty education level',{'educationLevel':[]})
scenario('education and position levels together',{'educationLevel':['Master','Doctorate'],'level':['mid-level','senior']})
for i in range(10):
    fs={c:random.sample(sorted(j[c].unique()),min(2,j[c].nunique())) for c in random.sample(['status','gender','country','sector','level'],2)}
    scenario('mixed '+str(i),fs,basis=random.choice(['birth_year','study_start','study_end','study_overlap']),lo=1910 if i%2 else 1935,hi=1940,unknown=bool(i%2))
expected={'bipartite_nodes':pd.read_csv(root/'tables/bipartite_nodes.csv').to_dict('records'),'projection_nodes':pd.read_csv(root/'tables/employer_nodes.csv').to_dict('records'),'bipartite_edges':len(pd.read_csv(root/'tables/bipartite_edges.csv')),'sankey_people':pd.read_csv(root/'tables/sankey_individual_bridges.csv').NameID.nunique(),'projection_edges':len(pd.read_csv(root/'tables/employer_edges.csv'))}
(root/'validation_cases.json').write_text(json.dumps({'cases':tests,'expected':expected}))
